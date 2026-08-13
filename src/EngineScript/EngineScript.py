import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import EngineScript.FileClass as fc


class Engine:
    def __init__(self, dataBase):
        if getattr(sys, 'frozen', False):
            self.__localPath = os.path.dirname(os.path.abspath(__file__)) # папка в которой лежит скрипт
        else:
            self.__localPath = Path(__file__).resolve().parent
        self.__workPath = self.__localPath

        self.__dataBase = dataBase

        self.__cashSearchFiles = []

        self.__CONFIG_FILE_NAME = "config.json"
        self.__DEFAULT_CONFIG = {
            "countStarts": 0,
            "batchSize": 500
        }
        self.__settings = self.__DEFAULT_CONFIG

        self.__createConfig()

        self.__hasher = hashlib.sha256()

        # КОНЕЦ ИНИЦИАЛИЗАЦИИ
        self.__addCountStarts()


    ''' getters '''
    def getLocalPath(self):
        return self.__localPath


    def getSettigs(self):
        return self.__settings


    def getWorkPath(self):
        return self.__workPath


    def getCashSearchFiles(self):
        return self.__cashSearchFiles

    
    def getSizechunck(self):
        sizeChunck = self.__settings.get("batchSize")
        if sizeChunck != None:
            return sizeChunck
        print("Файл настроек поврежден")
        return

    ''' setters '''
    def setWorkPath(self, workPath):
        self.__workPath = workPath


    ''' Вспомогательные функции '''
    def __readFiles(self, path):
        if path not in (None, ""):
            self.__workPath = Path(path)
        elif not hasattr(self, "__workPath") or self.__workPath is None:
            self.__workPath = Path.cwd()

        all_files = []

        def _find_recursive(current_dir):
            for item in current_dir.iterdir():
                if item.is_file():
                    all_files.append(item)
                elif item.is_dir():
                    _find_recursive(item)

        _find_recursive(self.__workPath)

        return all_files


    def __readInfoFiles(self, fileList, format):

        fileListData = []

        for file in fileList:
            #print(file, flush=True)
            fullPath = file.resolve()
            statInfo = file.stat()
            fileName = file.name
            extension = file.suffix
            sizeBytes = statInfo.st_size
            modified = datetime.fromtimestamp(statInfo.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            hash = self.__getFileSha256(fullPath)

            currentFile = fc.File(fileName, fullPath, sizeBytes, extension, modified, hash)

            if extension == format or format == "":
                fileListData.append(currentFile)

        return fileListData


    def __createConfig(self):
        if not os.path.exists(self.__CONFIG_FILE_NAME):
            print("=====Создание файла конфигурации=====")

            with open(self.__CONFIG_FILE_NAME, "w", encoding='utf-8') as f:
                json.dump(self.__DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)

        else:
            with open(self.__CONFIG_FILE_NAME, 'r', encoding='utf-8') as f:
                print("=====Загрузка настроек=====")
                self.__settings = json.load(f)


    def __getFileSha256(self, filePath):
        try:
            hasher = hashlib.sha256() 

            with open(filePath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            return "Файл не найден"


    def __addCountStarts(self):
        self.__settings["countStarts"] += 1

        with open(
            self.__CONFIG_FILE_NAME, "w", encoding="utf-8"
        ) as f:
            json.dump(self.__settings, f, indent=4, ensure_ascii=False)


    def __addFileInDatabase(self, fileInfo):
        sizeChunk = self.getSizechunck()
        filePackeges = [fileInfo[i:i + sizeChunk] for i in range(0, len(fileInfo), sizeChunk)]

        print(f"Всего файлов добавляется в базу: {len(fileInfo)} | Разбиты на {len(filePackeges)} пакетов")
        countAddPackege = 0

        for pack in filePackeges:
            if self.__dataBase.parseFiles(pack, "Сканирование"):
                countAddPackege += 1

        print(f"Успешно обработано: {countAddPackege} пакетов")
  

    def readAndSaveFileIndexes(self, path, format=""):

        print("=====Чтение файлов каталога=====")
        fileList = self.__readFiles(path)
        print("успешно")

        print("=====Создание классов файлов=====")
        fileInfo = self.__readInfoFiles(fileList, format)
        print("успешно")

        print("=====Добавление файлов в базу...======")
        self.__addFileInDatabase(fileInfo)

    
    def showAllFilesInDataBase(self):

        print("=====Список актуальных файлов базы данных=====")
        self.__dataBase.displayAllFiles()

        timeLastSession = self.__dataBase.getLastSession()
        print(f"Последняя сессия сканирования была: {timeLastSession}")


    def showAllOperation(self):

        print("=====Список всех операций=====")
        self.__dataBase.displayAllOperation()



