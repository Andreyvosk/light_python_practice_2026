import os
import sys
from pathlib import Path
from datetime import datetime
import EngineScript.FileClass as fc


class Engine:
    def __init__(self, dataBase):
        if getattr(sys, 'frozen', False):
            self.__localPath = os.path.dirname(sys.executable) # папка в которой лежит скрипт
        else:
            self.__localPath = Path(__file__).resolve().parent
        self.__workPath = self.__localPath

        self.__dataBase = dataBase

    ''' getters '''
    def getLocalPath(self):
        return self.__localPath


    def getWorkPath(self):
        return self.__workPath


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
            print(file, flush=True)
            statInfo = file.stat()
            fileName = file.name
            extension = file.suffix
            sizeBytes = statInfo.st_size
            modified = datetime.fromtimestamp(statInfo.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            currentFile = fc.File(fileName, str(file.resolve()), sizeBytes, extension, modified)

            fileListData.append(currentFile)
            print("\033[K", end="")

        return fileListData


    def __saveFilesInBase(self, fileList):
        for file in fileList:
            if(self.__dataBase.addFile(file)):
                print(f"Файл: {file.getName} \t успешно добавлен в систему")
            else:
                print(f"!!Файл: {file.getName} \t НЕ ДОБАВЛЕН")


    ''' Функции для индексации '''
    def readAndSaveFileIndexes(self, path):

        print("=====Чтение файлов каталога=====")
        fileList = self.__readFiles(path)
        print("=====Успешное чтение файла=====")

        print("=====Создание классов файлов=====")
        fileInfo = self.__readInfoFiles(fileList)
        print("=====Успешно созданы классы файлов=====")

        print("=====Добавление файлов в базу...======")
        for file in fileInfo:
            self.__dataBase.addNewFile(file)
        print("=====Файлы успешно добавлены в базу")






