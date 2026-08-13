import EngineScript.EngineScript as es
import SQLscripts.database as db
import argparse
from datetime import datetime

class TerminalApp:
    def __init__(self):
        self.__mainDataBase = db.DataBase()

        self.__mainEngine = es.Engine(self.__mainDataBase)

        self.__parser = argparse.ArgumentParser()

        self.__setArg()


    def __setArg(self):
        self.__parser.add_argument(
            "-f",
            "--filter",
            dest="filter",
            type=str,
            default="",
            help="Фильтр для поиска файлов"
        )

        self.__parser.add_argument(
            "-d",
            "--dir",
            dest="dir_path",
            type=str,
            help="путь к рабочей дирректории"
        )

        self.__parser.add_argument(
            "-b",
            "--backup",
            dest="backup",
            type=str,
            default="",
            help="Путь к файлу бэкапа"
        )

        self.__parser.add_argument(
            "-c",
            "--compare",
            dest="compare",
            type=str,
            nargs=2,
            default="",
            help="Путь к директории для сравнения файлов"
        )

        self.__parser.add_argument(
            "-i",
            "-info",
            dest="info",
            action='store_true',
            help="Информация"
        )

        self.__parser.add_argument(
            "-s",
            "--session",
            dest="session_id",
            type=int,
            help="Показать информацию о конкретной сессии сканирования"
        )

        self.__parser.add_argument(
            "-l",
            "--last",
            dest="last_sessions",
            type=int,
            default=5,
            help="Показать последние N сессий (по умолчанию 5)"
        )

        self.__parser.add_argument(
            "-stats",
            "--statistics",
            dest="statistics",
            action='store_true',
            help="Показать общую статистику базы данных"
        )


    def start(self):
        args = self.__parser.parse_args()
        direct = args.dir_path
        info = args.info
        statFlag = args.statistics

        if info:
            self.__mainEngine.showAllFilesInDataBase()
            return

        if statFlag:
            self.__mainEngine.showAllOperation()
            return

        self.__mainEngine.readAndSaveFileIndexes(direct)
        

        