import EngineScript.EngineScript as es
import SQLscripts.database as db
import argparse

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


    def start(self):

        args = self.__parser.parse_args()
        filter = ""
        dir = ""
        flagStart = False

        if args.filter != "":
            filter = args.filter

        if args.dir_path != None:
            flagStart = True
            dir = args.dir_path
            print(f"Рабочая папка: {args.dir_path}")

            self.__mainEngine.readAndSaveFileIndexes(dir, filter)

        if args.backup != "":
            self.__mainDataBase.createBackup(args.backup)
            flagStart = True

        if args.compare:
            firstDir, secondDir = args.compare
            self.__mainEngine.comparePaths(firstDir, secondDir)
            flagStart = True

        if args.info:
            flagStart = True
            print(self.__mainEngine.getSettigs())

        if flagStart != True:
            print("Путь не указан, сканирование отменено")




