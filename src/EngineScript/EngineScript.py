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
        fileList = [str(f) for f in folder.rglob('*') if f.is_file()]

        return fileList


    def __readInfoFiles(self, fileList):

        fileListData = []

        for file in fileList:
            statInfo = file.stat()
            fileName = file.name
            extension = file.suffix
            sizeBytes = statInfo.st_size
            modified = datetime.fromtimestamp(statInfo.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            currentFile = fc.File(fileName, str(file.resolve()), sizeBytes, extension, modified)

            fileListData.append(currentFile)

        return fileListData


    def __saveFilesInBase(self, fileList):
        pass # переделать добавление файлов в базу


    ''' Функции для индексации '''
    def readAndSaveFileIndexes(self, path):

        print("=====Чтение файлов каталога=====")
        fileList = self.__readFiles(path)
        print("=====Успешное чтение файла=====")

        print("=====Создание классов файлов=====")
        fileInfo = self.__readInfo(fileList)
        print("=====Успешно созданы классы файлов=====")





