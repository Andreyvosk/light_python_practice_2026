import os
import sys
import json
from pathlib import Path
from datetime import datetime
import EngineScript.FileClass as fc
import EngineScript.LoadingAnimation as la


class Engine:
    def __init__(self, dataBase):
        if getattr(sys, 'frozen', False):
            self.__localPath = os.path.dirname(sys.executable) # папка в которой лежит скрипт
        else:
            self.__localPath = Path(__file__).resolve().parent
        self.__workPath = self.__localPath

        self.__dataBase = dataBase

        self.__cashSearchFiles = []

        self.__animation = la.LoadingAnimation()

        self.__CONFIG_FILE_NAME = "config.json"
        self.__DEFAULT_CONFIG = {
            "countStarts": 0
        }
        self.__settings = self.__DEFAULT_CONFIG

        self.__createConfig()

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


    def __readInfoFiles(self, fileList):

        fileListData = []

        for file in fileList:
            #print(file, flush=True)
            statInfo = file.stat()
            fileName = file.name
            extension = file.suffix
            sizeBytes = statInfo.st_size
            modified = datetime.fromtimestamp(statInfo.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            currentFile = fc.File(fileName, str(file.resolve()), sizeBytes, extension, modified)

            fileListData.append(currentFile)
            #print("\033[K", end="")

        return fileListData


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

    ''' Функции для индексации '''
    def readAndSaveFileIndexes(self, path):

        print("=====Чтение файлов каталога=====")
        self.__animation.start()
        fileList = self.__readFiles(path)
        self.__animation.stop()

        print("=====Создание классов файлов=====")
        self.__animation.start()
        fileInfo = self.__readInfoFiles(fileList)
        self.__animation.stop()

        print("=====Добавление файлов в базу...======")
        self.__animation.start()
        for file in fileInfo:
            file.display()
            self.__dataBase.addNewFile(file)
        self.__animation.stop()













