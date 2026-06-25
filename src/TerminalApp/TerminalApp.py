import EngineScript.EngineScript as es
import SQLscripts.database as db
import sys

class TerminalApp:
    def __init__(self):
        self.__mainDataBase = db.DataBase()

        self.__mainEngine = es.Engine(self.__mainDataBase)


    def start(self):
        print("Программа успешно запустилась, рабочий путь:", str(self.__mainEngine.getWorkPath()))

        answer = input("Перечитать файлы? (все/фильтр)")

        if answer.strip() == "все":
            self.__mainEngine.readAndSaveFileIndexes("", "")
        if answer.strip() == "фильтр":
            format = input("Введите формат читаемых файлов: ")
            self.__mainEngine.readAndSaveFileIndexes("", format)

        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                self.__completeCommand(line.strip())
        except KeyboardInterrupt:
            print("Программа неожиданно завершиласб")


    def __completeCommand(self, line):
        if line == "help":
            self.__help()
        if line == "reserch":
            pass
        if line == "showall":
            self.__showall()
        if "find" in line:
            self.__findFile()
        if line == "deldup":
            self.__deldup()
        if line == "backup":
            self.__backup()
        if line == "comapre":
            self.__compare()

    ''' Команды для выполнения в терминале '''
    def __help(self):
        print('''
        ===== СПРАВОЧНАЯ ИНФОРМАЦИЯ О ДОСТУПНЫХ КОММАНДАХ =====
        1. help - вызов справочной информации.
        2. reserch - перечитать файлы текущего каталога.
        3. showall - показать все файлы БД.
        4. find - Найти путь файла. (find [Имя файла])
        5. deldup - Удалить дубликаты.
        ''')


    def __showall(self):
        files = self.__mainDataBase.requestAllFiles()

        for file in files:
            print(f"{file[1]}                           {file[3]}                             {file[7]}")


    def __findFile(self, line):
        fileName = line[6::]

        result = self.__mainDataBase.findFile(fileName)

        if len(result) < 1:
            print("Этот файл не был проиндексирован")

        for file in result:
            print(f"Путь к файлу: {file[0]}")


    def __deldup(self):
        self.__mainDataBase.removeDuplicates()


    def __backup(self):
        self.__mainDataBase.createBackup()


    def __compare(self):
        self.__mainDataBase.compareWithBackup()


