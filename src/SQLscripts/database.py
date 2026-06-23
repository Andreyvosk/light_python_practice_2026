import sqlite3
from datetime import datetime
import os
from pathlib import Path
import EngineScript.FileClass as fc

class DataBase:
    def __init__(self, catalogData="indexer.db"):

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

        self.__catalogDataBase = os.path.join(CURRENT_DIR, catalogData)

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
            CREATE TABLE IF NOT EXISTS files (
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
            self.__flagInitDataBase = True

        self.__mainConnect.commit()


    def __del__(self):
        self.__mainConnect.commit()
        self.__mainConnect.close()


    ''' geters '''
    def getCatalogDataBase(self):
        return self.__catalogDataBase


    def getLastAddFile(self):
        self.__mainCursor.execute('''
            SELECT C_ID, C_FILE_NAME, C_CREATE_DATE
            FROM files
            ORDER BY C_CHANGE_DATE DESC
            LIMIT 1;
        ''')

        return self.__mainCursor.fetchone()


    def getAllExtension(self):

        sqlRequestText = "SELECT * FROM formats"

        self.__mainCursor.execute(sqlRequestText)

        return self.__mainCursor.fetchone()


    ''' Добавление данных в базу '''
    def addNewFile(self, file):
        if isinstance(file, fc.File):

            sqlFormatText = "INSERT INTO files (C_FILE_NAME, C_FULL_NAME, C_CHANGE_DATE, C_CREATE_DATE, C_FORMAT_ID, C_HASH_SUM) VALUES (?, ?, ?, ?, ?, ?);"

            formatName = file.getExtension()
            filePath = file.getFullName()
            currentTimeString = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            #print(f"Файл: {file.getName()}\t|\tформат файла: {formatName}")

            fileFormat = self.__findFormatID(formatName, filePath)

            if fileFormat != -1:
                self.__mainCursor.execute(sqlFormatText, (file.getName(), str(file.getFullName()), currentTimeString, currentTimeString, fileFormat, file.getHash()))

            self.__mainConnect.commit()

            return True
        else:
            return False


    def addNewFormat(self, formatName, filePath):
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
                self.addNewFormat(formatName, filePath)
                return self.__findFormatID(formatName, filePath)
            else:
                return result[0]

        else:
            return -1


    def requestAllFiles(self):
        sqlRequest = "SELECT f.*, fm.F_NAME, fm.F_ISBINARY FROM files f LEFT JOIN formats fm ON f.C_FORMAT_ID = fm.F_ID;"
        self.__mainCursor.execute(sqlRequest)

        result = self.__mainCursor.fetchall()

        return result


    def __deleteFile(self, hashToDelete):
        sqlDelete = "DELETE FROM files WHERE C_HASH_SUM = ?"

        self.__mainCursor.execute(sqlDelete, (hashToDelete,))

        self.__mainConnect.commit()


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


    def __findFilesInBase(self, fileList):
        if not fileList:
            return []

        batchList = [file.getHash() for file in fileList]
        placeholders = ",".join(["?"] * len(fileList))

        sqlRequestText = (
            f"SELECT C_HASH_SUM FROM files WHERE C_HASH_SUM IN ({placeholders})"
        )

        self.__mainCursor.execute(sqlRequestText, batchList)
        rows = self.__mainCursor.fetchall()

        existing_hashes = {row[0] for row in rows}

        resultList = []

        for file in fileList:
            if file.getHash() not in existing_hashes:
                resultList.append(file)

        return resultList


    def findFiles(self, fileList):
        resultFileList = []

        for i in range(len(fileList)):
            currentList = fileList[i]
            resultFileList.extend(self.__findFilesInBase(currentList))

        return resultFileList



















