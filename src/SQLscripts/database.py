import sqlite3

class DataBase:
    def __init__(self, catalogData):
        self.__catalogDataBase = catalogData
        self.__mainConnect = sqlite3.connect(self.__catalogDataBase)

        self.__mainCursor = self.__mainConnect.cursor();

        # Создание основных таблиц базы данной
        self.__mainCursor.execute('''
        CREATE TABLE IF NOT EXISTS catalogData (
            CD_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CD_NAME_CATALOG TEXT NOT NULL,
            CD_FULL_NAME TEXT NOT NULL
            )
        ''')


    def __del__(self):
        self.__mainConnect.commit()
        self.__mainConnect.close()


    def getCatalogDataBase(self):
        return self.__catalogDataBase

