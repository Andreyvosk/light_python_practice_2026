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


    def getSettigs(self):
        return self.__settings


    def getWorkPath(self):
        return self.__workPath


    def getCashSearchFiles(self):
        return self.__cashSearchFiles


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


    def comparePaths(self, firstPath, secondPath, extension_filter, historyManager=None):
        p1 = Path(firstPath).resolve()
        p2 = Path(secondPath).resolve()

        startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"Путь: {p1} - основной | Путь сравнения: {p2}")

        if not (p1.exists() and p1.is_dir() and p2.exists() and p2.is_dir()):
            print("Один или оба путей не существуют или не являются директориями")
            return

        ext = None
        if extension_filter and extension_filter != "":
            ext = extension_filter.lower()
            if not ext.startswith("."):
                ext = "." + ext

        def filter_by_extension(file_list, ext_filter):
            if ext_filter is None:
                return file_list
            return [f for f in file_list if f.suffix.lower() == ext_filter]

        print("=====Чтение файлов директорий=====")
        firstFileList = self.__readFiles(p1)
        secondFileList = self.__readFiles(p2)

        firstFileList = filter_by_extension(firstFileList, ext)
        secondFileList = filter_by_extension(secondFileList, ext)

        if ext:
            print(f"Фильтр по расширению: {ext}")

                # Статистика для истории
        cntChanged = 0      # Измененные файлы (хэш отличается)
        cntNew = 0          # Новые файлы (есть в первой, нет во второй)
        cntDeleted = 0      # Удаленные файлы (есть во второй, нет в первой)
        cntIdentical = 0    # Идентичные файлы

                # Создаем сессию сравнения
        if historyManager:
            sessionId = historyManager.createSession(
                startTime=startTime,
                typeScan="COMPARE",
                pathScan=f"{p1} ↔ {p2}",
                filter=ext if ext else "",
                cntFiles=len(firstFileList) + len(secondFileList),
                cntAdded=0,
                cntUpdated=0,
                cntDeleted=0,
                status="IN_PROGRESS"
            )

        matched_in_second = []
        changes = []  # Список изменений для записи в историю

        print("=====Сравнение файлов=====")

                # Сравниваем файлы из первой директории
        for file in firstFileList:
            try:
                relFirst = file.relative_to(p1)
            except ValueError:
                continue

            firstHash = self.__getFileSha256(file)
            if firstHash is None:
                continue

            matched = False
            for secFile in secondFileList:
                try:
                    relSecond = secFile.relative_to(p2)
                except ValueError:
                    continue

                secHash = self.__getFileSha256(secFile)
                if secHash is None:
                    continue

                if relFirst == relSecond:
                    if firstHash != secHash:
                        print(f"[Изменен] Файл: {relFirst}")
                        cntChanged += 1
                        changes.append({
                            'file_name': file.name,
                            'file_path': str(relFirst),
                            'hash': secHash,
                            'operation': 'UPDATED',
                            'details': f"Хэш изменен: {firstHash[:8]}... → {secHash[:8]}..."
                        })
                    else:
                        cntIdentical += 1
                        changes.append({
                            'file_name': file.name,
                            'file_path': str(relFirst),
                            'hash': firstHash,
                            'operation': 'IDENTICAL',
                            'details': "Файл не изменился"
                        })

                    matched = True
                    matched_in_second.append(secFile)
                    break

            if not matched:
                    # Ищем файл с таким же хэшем во второй директории
                for secFile in secondFileList:
                    if secFile in matched_in_second:
                        continue
                    secHash = self.__getFileSha256(secFile)
                    if secHash is None:
                        continue

                    if firstHash == secHash:
                        matched = True
                        matched_in_second.append(secFile)
                        break

            if not matched:
                print(f"[Новый (есть в первой, нет во второй)] Файл: {file.name} ({relFirst})")
                cntNew += 1
                changes.append({
                    'file_name': file.name,
                    'file_path': str(relFirst),
                    'hash': firstHash,
                    'operation': 'ADDED',
                    'details': "Файл отсутствует во второй директории"
                })

                # Проверяем файлы, которые есть во второй директории, но нет в первой
        for secFile in secondFileList:
            if secFile not in matched_in_second:
                try:
                    rel = secFile.relative_to(p2)
                    print(f"[Удален (есть во второй, нет в первой)] Файл: {rel}")
                    cntDeleted += 1
                    secHash = self.__getFileSha256(secFile)
                    changes.append({
                        'file_name': secFile.name,
                        'file_path': str(rel),
                        'hash': secHash if secHash else "N/A",
                        'operation': 'DELETED',
                        'details': "Файл отсутствует в первой директории"
                    })
                except ValueError:
                    print(f"[Удален] Файл: {secFile.name}")
                    cntDeleted += 1
                    changes.append({
                        'file_name': secFile.name,
                        'file_path': str(secFile),
                        'hash': "N/A",
                        'operation': 'DELETED',
                        'details': "Файл отсутствует в первой директории"
                        })

                # Записываем изменения в историю
        if historyManager and changes:
            for change in changes:
                        # Пропускаем IDENTICAL, если не хотим их записывать
                if change['operation'] == 'IDENTICAL':
                    continue

                        # Для UPDATED используем хэш из второй директории
                hash_to_save = change['hash'] if change['hash'] != "N/A" else "UNKNOWN"

                historyManager.addChangeRecord(
                    fileName=change['file_name'],
                    filePath=change['file_path'],
                    fileHash=hash_to_save,
                    operationType=change['operation'],
                    timeChange=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )

            # Обновляем сессию с итоговыми данными
        if historyManager:
            sessionId = historyManager.getCurrentSessionId()
            if sessionId:
                updateSessionSql = '''UPDATE scan_sessions
                SET SS_CNT_ADDED = ?, SS_CNT_UPDATED = ?, SS_CNT_DELETED = ?, SS_STATUS = ?
                WHERE SS_ID = ?
                '''
                cursor = self.__dataBase.getCursor()
                cursor.execute(updateSessionSql, (
                    cntNew, cntChanged, cntDeleted, "COMPLETED", sessionId
                ))
                self.__dataBase.getConnect().commit()

                # Выводим итоговую статистику
        print(f"\n{'='*60}")
        print(f"📊 ИТОГИ СРАВНЕНИЯ:")
        print(f"{'='*60}")
        print(f"   📄 Идентичных файлов:  {cntIdentical}")
        print(f"   ✏️ Измененных файлов:  {cntChanged}")
        print(f"   ➕ Новых файлов:       {cntNew}")
        print(f"   🗑 Удаленных файлов:   {cntDeleted}")
        print(f"   📊 Всего изменений:    {cntChanged + cntNew + cntDeleted}")
        print(f"{'='*60}")


    ''' Функции для индексации '''
    def readAndSaveFileIndexes(self, path, format, historyManager=None):
        startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print("=====Чтение файлов каталога=====")
        self.__animation.start()
        fileList = self.__readFiles(path)
        self.__animation.stop()

        print("=====Создание классов файлов=====")
        self.__animation.start()
        fileInfo = self.__readInfoFiles(fileList, format)
        self.__animation.stop()

        totalFiles = len(fileInfo)
        cntAdded = 0
        cntUpdated = 0
        cntDeleted = 0

        print("=====Добавление файлов в базу...======")
        self.__animation.start()

        if historyManager:
            historyManager.createSession(
                startTime=startTime,
                typeScan="FULL_SCAN",
                pathScan=path,
                filter=format,
                cntFiles=totalFiles,
                cntAdded=0,
                cntUpdated=0,
                cntDeleted=0,
                status="IN_PROGRESS"
            )

        for file in fileInfo:
            file.display()
            result = self.__dataBase.addNewFile(file, historyManager)

            if result == 'ADDED':
                cntAdded += 1
            elif result == 'UPDATED':
                cntUpdated += 1

        deletedCount = self.__dataBase.removeDuplicates()
        cntDeleted = deletedCount

        self.__animation.stop()

        if historyManager:
            sessionId = historyManager.getCurrentSessionId()
            updateSessionSql = '''UPDATE scan_sessions
            SET SS_CNT_ADDED = ?, SS_CNT_UPDATED = ?, SS_CNT_DELETED = ?, SS_STATUS = ?
            WHERE SS_ID = ?
            '''
            self.__dataBase.getCursor().execute(updateSessionSql, (
                cntAdded, cntUpdated, cntDeleted, "COMPLETED", sessionId
            ))
            self.__dataBase.getConnect().commit()

        print(f"Добавлено: {cntAdded}, Обновлено: {cntUpdated}, Удалено: {cntDeleted}")













