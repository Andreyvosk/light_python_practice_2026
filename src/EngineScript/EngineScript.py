import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import EngineScript.FileClass as fc
import EngineScript.LoadingAnimation as la


class Engine:
    def __init__(self, dataBase):
        if getattr(sys, 'frozen', False):
            self.__localPath = os.path.dirname(os.path.abspath(__file__)) # папка в которой лежит скрипт
        else:
            self.__localPath = Path(__file__).resolve().parent
        self.__workPath = self.__localPath

        self.__dataBase = dataBase

        self.__cashSearchFiles = []

        self.__animation = la.LoadingAnimation()

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


    def getWorkPath(self):
        return self.__workPath


    def getCashSearchFiles(self):
        return self.__cashSearchFiles


    ''' setters '''
    def setWorkPath(self, workPath):
        self.__workPath = workPath


    ''' Вспомогательные функции '''
    def __readFiles(self, path):
        if not(path is None or path == ""):
            self.__workPath = path

        folder = Path(path)
        fileList = [f for f in folder.rglob('*') if f.is_file()]

        return fileList

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
            #print("\033[K", end="")

        fileListForFind = [fileListData[i : i + self.__settings["batchSize"]] for i in range(0, len(fileListData), self.__settings["batchSize"])]

        return self.__dataBase.findFiles(fileListForFind)


    def __saveFilesInBase(self, fileList):
        for file in fileList:
            if(self.__dataBase.addFile(file)):
                print(f"Файл: {file.getName} \t успешно добавлен в систему")
            else:
                print(f"!!Файл: {file.getName} \t НЕ ДОБАВЛЕН")


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
            with open(filePath, 'rb') as f:
                while chunk := f.read(8192):
                    self.__hasher.update(chunk)

            return self.__hasher.hexdigest()

        except FileNotFoundError:
            return "Файл не найден"


    def __addCountStarts(self):
        self.__settings["countStarts"] += 1

        with open(
            self.__CONFIG_FILE_NAME, "w", encoding="utf-8"
        ) as f:
            json.dump(self.__settings, f, indent=4, ensure_ascii=False)



    ''' Функции для индексации '''
    def readAndSaveFileIndexes(self, path, format):

        print("=====Чтение файлов каталога=====")
        self.__animation.start()
        fileList = self.__readFiles(path)
        self.__animation.stop()

        print("=====Создание классов файлов=====")
        self.__animation.start()
        fileInfo = self.__readInfoFiles(fileList, format)
        self.__animation.stop()

        print("=====Добавление файлов в базу...======")
        self.__animation.start()
        for file in fileInfo:
            file.display()
            self.__dataBase.addNewFile(file)
        self.__animation.stop()













