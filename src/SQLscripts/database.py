import sqlite3
from datetime import datetime
import os
from pathlib import Path
import EngineScript.FileClass as fc

class DataBase:
    def __init__(self, catalogData="indexer.db"):

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

        # Константы для операций
        self.__OP_RENAME = "Переименован"
        self.__OP_DELETE = "Удален"
        self.__OP_CHANGE = "Изменен"
        self.__OP_INSERT = "Добавлен"

        self.__catalogDataBase = os.path.join(CURRENT_DIR, catalogData)
        self.__dumpFile = os.path.join(CURRENT_DIR, "log.txt")

        self.__mainConnect = sqlite3.connect(self.__catalogDataBase)

        self.__mainCursor = self.__mainConnect.cursor();
        self.__flagInitDataBase = False

        if not(self.__flagInitDataBase):
            # Создание основных таблиц базы данной
            self.__mainCursor.execute('''
            PRAGMA foreign_keys = ON;
            ''')

            # 1. Таблийца форматов файлов
            self.__mainCursor.execute('''
            CREATE TABLE IF NOT EXISTS formats (
                F_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                F_NAME TEXT NOT NULL,
                F_ISBINARY BOOLEAN
                );
            ''')

            # 2. Таблица индексов файлов
            self.__mainCursor.execute('''
            CREATE TABLE IF NOT EXISTS currentFiles (
                C_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                C_FILE_NAME TEXT NOT NULL,
                C_FULL_NAME TEXT NOT NULL,
                C_CHANGE_DATE DATETIME NOT NULL,
                C_CREATE_DATE DATETIME NOT NULL,
                C_FORMAT_ID INTEGER,
                C_HASH_SUM VARCHAR(64) NOT NULL,
                FOREIGN KEY (C_FORMAT_ID) REFERENCES formats(F_ID)
                );
            ''')

            # 3. Таблица историй операций с файлами
            self.__mainCursor.execute('''
            CREATE TABLE IF NOT EXISTS operationHistory (
                OH_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                OH_OPERATION_TIME DATETIME NOT NULL,
                OH_FILE_ID INTEGER NOT NULL,
                OH_OPERATION_ID INTEGER NOT NULL,
                OH_INFO_CHANGE VARCHAR(64),
                OH_HASH VARCHAR(64),
                OH_FILE_NAME VARCHAR(255),
                FOREIGN KEY (OH_FILE_ID) REFERENCES currentFiles(C_ID)
                );
            ''')

            # 4. Таблица выполненных операций
            self.__mainCursor.execute('''
            CREATE TABLE IF NOT EXISTS completeOperation (
                CO_ID INTEGER PRIMARY KEY,
                CO_OPERATION_NAME VARCHAR(64) NOT NULL, 
                CO_START_TIME DATETIME NOT NULL,
                CO_END_TIME DATETIME NOT NULL
                );
            ''')

            self.__flagInitDataBase = True

        self.__mainConnect.commit()
        
        self.__idOperationCounter = self.__getCounterID()


    def __del__(self):
        self.__mainConnect.commit()
        self.__mainConnect.close()


    ''' geters '''
    def getCatalogDataBase(self):
        return self.__catalogDataBase


    def getAllExtension(self):

        sqlRequestText = "SELECT * FROM formats"

        self.__mainCursor.execute(sqlRequestText)

        return self.__mainCursor.fetchone()


    def getLastSession(self): 
        sqlText = "SELECT CO_END_TIME FROM completeOperation ORDER BY CO_ID DESC LIMIT 1"

        self.__mainCursor.execute(sqlText)

        return self.__mainCursor.fetchone()[0]


    ''' displayses '''
    def displayAllFiles(self):
        sqlRequest = "SELECT * FROM currentFiles"

        self.__mainCursor.execute(sqlRequest)
        resultRequest = self.__mainCursor.fetchall()

        for row in resultRequest:
            for element in row:
                print(f"{element} ", end="")
            print()


    def displayAllOperation(self):
        sqlText = "SELECT * FROM operationHistory"

        self.__mainCursor.execute(sqlText)
        resultRequest = self.__mainCursor.fetchall()

        for row in resultRequest:
            for element in row:
                print(f"{element} ", end="")
            print()


    ''' Добавление данных в базу '''
    def parseFiles(self, fileList, typeSession):
        startTime = datetime.now()

        self.__dump(f"\nНачало парса файлов: {startTime} | Тип сканирования: {typeSession}")

        for file in fileList:
            self.__dump(f"parseFiles: Поиск файла {file.getName()} в базе")
            if self.__findAndUpdateFileInBase(file) == False:
                self.__dump(f"parseFiles: Файл не найден, добавление файла в базу")
                self.__addNewFileInBase(file)
        # Записываем сессию сканирования
        sessionID = self.__idOperationCounter
        name = typeSession
        endTime = datetime.now()

        sqlText = '''INSERT INTO completeOperation (CO_ID, CO_OPERATION_NAME, CO_START_TIME, CO_END_TIME)
                     VALUES (?, ?, ?, ?)
                  '''

        self.__mainCursor.execute(sqlText, (sessionID, name, startTime, endTime))
        self.__upIDCounter()
        self.__mainConnect.commit()
        return True


    def __addNewFormat(self, formatName, filePath):
        sqlFormatText = "INSERT INTO formats (F_NAME, F_ISBINARY) VALUES (?, ?);"

        self.__mainCursor.execute(sqlFormatText, (formatName, self.__isBinaryFile(filePath)))

        self.__mainConnect.commit()


    ''' Запрсы '''
    def __findFormatID(self, formatName, filePath):
        if isinstance(formatName, str):
            sqlRequest = "SELECT F_ID FROM formats WHERE F_NAME = ? LIMIT 1;"
            self.__mainCursor.execute(sqlRequest, (formatName,))

            result = self.__mainCursor.fetchone()

            if result is None:
                self.__addNewFormat(formatName, filePath)
                return self.__findFormatID(formatName, filePath)
            else:
                return result[0]

        else:
            return -1
        

    def __findAndUpdateFileInBase(self, file):
        fileFullName = str(file.getFullName())
        fileHash = file.getHash()

        requestForName = '''SELECT 
                                C_ID,
                                C_FILE_NAME,
                                C_FULL_NAME,
                                C_HASH_SUM
                            FROM 
                                currentFiles
                            WHERE 
                                C_FULL_NAME = ?
                            LIMIT 1;
                         '''

        requestForHash = '''SELECT 
                                C_ID,
                                C_FILE_NAME,
                                C_FULL_NAME,
                                C_HASH_SUM
                            FROM
                                currentFiles
                            WHERE
                                C_HASH_SUM = ?
                            LIMIT 1;
                         '''
        
        self.__mainCursor.execute(requestForName, (fileFullName, ))
        resultFindName = self.__mainCursor.fetchone()

        self.__mainCursor.execute(requestForHash, (fileHash, ))
        resultFindHash = self.__mainCursor.fetchone()

        if resultFindName != None:
            if resultFindName[3] == fileHash:
                return True
            else: 
                self.__changeFile(self.__OP_CHANGE, file, resultFindName[0])
                return True
        elif resultFindHash != None:
            if resultFindHash[2] == fileFullName:
                return True
            else:
                self.__changeFile(self.__OP_RENAME, file, resultFindHash[0])
                return True
        else:
            return False
                

    ''' Вспомогательные функции '''
    def __isBinaryFile(self, filePath):
        try:
            with open(filePath, 'r', encoding='utf-8') as f:
                chunk = f.read(1024)

                if '\x00' in chunk:
                    return True

                return False
        except UnicodeDecodeError:
            return True
        except Exception as e:
            print(f"Ошибка при чтении файла {filePath}: {e}")
            return False


    def __addOperationInBase(self, fileID, typeOperation, file):
        fileHash = file.getHash()
        fileName = file.getName()
        fileFullName = file.getFullName()
        operationTime = datetime.now()
        operationId = self.__idOperationCounter

        sqlText = '''INSERT INTO operationHistory (OH_OPERATION_TIME, OH_FILE_ID, OH_OPERATION_ID, OH_INFO_CHANGE, OH_HASH, OH_FILE_NAME)
                     VALUES (?, ?, ?, ?, ?, ?)
                  '''
        self.__mainCursor.execute(sqlText, (operationTime, fileID, operationId, typeOperation, fileHash, fileName))


    def __changeFile(self, statusFile, file, idFile):
        updateText = '''UPDATE 
                            currentFiles
                        SET 
                            C_FULL_NAME = ?,
                            C_HASH_SUM = ?,
                            C_FILE_NAME = ?,
                            C_CHANGE_DATE = ?
                        WHERE 
                            C_ID = ?
                     '''
        
        nowTime = datetime.now()
        self.__mainCursor.execute(updateText, (file.getFullName(), file.getHash(), file.getName(), nowTime, idFile))
        self.__mainConnect.commit()

        self.__addOperationInBase(idFile, statusFile, file)


    def __getCounterID(self):
        self.__mainCursor.execute("SELECT CO_ID FROM completeOperation ORDER BY CO_ID DESC LIMIT 1 ")

        lastID = self.__mainCursor.fetchone()
        
        if lastID is None:
            return 0
        return lastID[0] + 1

    
    def __upIDCounter(self):
        self.__idOperationCounter += 1


    def __addNewFileInBase(self, file):
        sqlText = '''INSERT INTO currentFiles (C_FILE_NAME, C_FULL_NAME, C_CHANGE_DATE, C_CREATE_DATE, C_FORMAT_ID, C_HASH_SUM)
                     VALUES (?, ?, ?, ?, ?, ?)
                  '''

        nowTime = datetime.now()

        self.__mainCursor.execute(sqlText, (file.getName(), file.getFullName(), nowTime, nowTime, self.__findFormatID(file.getExtension(), file.getFullName()), file.getHash()))
        idFile = self.__mainCursor.lastrowid

        self.__dump(f"addNewFileInBase: Файл {file.getName()} добавлен в базу ID {idFile}")
        self.__mainConnect.commit()

        self.__addOperationInBase(idFile, self.__OP_INSERT, file)


    def __dump(self, text):
        try:
            with open(self.__dumpFile, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except:
            print("Файл дампа отсутсвует")















