import EngineScript.EngineScript as es
import SQLscripts.database as db
import HistoryManager.HistoryManager as hm
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
        filter = ""
        dir = ""
        flagStart = False

            # Создаем HistoryManager для работы с историей
        self.__historyManager = hm.HistoryManager(self.__mainDataBase)

            # Показываем статистику
        if args.statistics:
            flagStart = True
            self.showStatistic()

            # Показываем информацию о сессии
        if args.session_id:
            flagStart = True
            self.showScanInfo(session_id=args.session_id)

            # Показываем последние сессии
        if args.last_sessions and not args.session_id:
            flagStart = True
            self.showScanInfo(limit=args.last_sessions)

        if args.filter != "":
            filter = args.filter

        if args.dir_path != None:
            flagStart = True
            dir = args.dir_path
            print(f"Рабочая папка: {args.dir_path}")
                # Передаем historyManager в движок
            self.__mainEngine.readAndSaveFileIndexes(dir, filter, self.__historyManager)

        if args.backup != "":
            self.__mainDataBase.createBackup(args.backup)
            flagStart = True

        if args.compare:
            firstDir, secondDir = args.compare
            self.__mainEngine.comparePaths(firstDir, secondDir, filter)
            flagStart = True

        if args.info:
            flagStart = True
            print(self.__mainEngine.getSettigs())

        if flagStart != True:
            print("Путь не указан, сканирование отменено")

    def showScanInfo(self, session_id=None, limit=10):

        cursor = self.__mainDataBase.getCursor()

        if session_id:

            sql = '''SELECT
                SS_ID, SS_START_TIME, SS_END_TIME, SS_TYPE_SCAN,
                    SS_PATH, SS_FILTER, SS_FILES_SCANNED,
                    SS_CNT_ADDED, SS_CNT_UPDATED, SS_CNT_DELETED, SS_STATUS
                FROM scan_sessions
                WHERE SS_ID = ?'''
            cursor.execute(sql, (session_id,))
            session = cursor.fetchone()

            if not session:
                print(f"❌ Сессия с ID {session_id} не найдена")
                return

            self.__printSessionInfo(session)

            self.__printSessionChanges(session_id)

        else:

            sql = '''SELECT
                    SS_ID, SS_START_TIME, SS_END_TIME, SS_TYPE_SCAN,
                    SS_PATH, SS_FILTER, SS_FILES_SCANNED,
                    SS_CNT_ADDED, SS_CNT_UPDATED, SS_CNT_DELETED, SS_STATUS
                FROM scan_sessions
                ORDER BY SS_ID DESC
                LIMIT ?'''
            cursor.execute(sql, (limit,))
            sessions = cursor.fetchall()

            if not sessions:
                print("📭 История сканирований пуста")
                return

            print(f"\n{'='*80}")
            print(f"📊 ПОСЛЕДНИЕ {len(sessions)} СЕССИЙ СКАНИРОВАНИЯ")
            print(f"{'='*80}\n")

            for session in sessions:
                self.__printSessionInfo(session, compact=True)
                print("-" * 80)

    def __printSessionInfo(self, session, compact=False):

        (ss_id, start_time, end_time, type_scan, path,
        filter_str, files_scanned, added, updated, deleted, status) = session

        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        duration = end_dt - start_dt

            # Статус с эмодзи
        status_emoji = {
                    'COMPLETED': '✅',
                    'IN_PROGRESS': '🔄',
                    'FAILED': '❌',
                    'CANCELLED': '⛔'
                }.get(status, '❓')

        if compact:
            print(f"📌 Сессия #{ss_id} {status_emoji}")
            print(f"   📅 {start_time} → {end_time} (⏱ {duration})")
            print(f"   📁 {path}")
            print(f"   🔍 Фильтр: {filter_str if filter_str else 'Нет'}")
            print(f"   📄 Файлов: {files_scanned} | ➕ {added} | ✏️ {updated} | 🗑 {deleted}")
        else:
            print(f"\n{'='*80}")
            print(f"📌 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О СЕССИИ #{ss_id}")
            print(f"{'='*80}")
            print(f"🔄 Статус: {status} {status_emoji}")
            print(f"📅 Время начала:   {start_time}")
            print(f"📅 Время окончания: {end_time}")
            print(f"⏱ Длительность:   {duration}")
            print(f"📁 Путь:          {path}")
            print(f"🔍 Фильтр:        {filter_str if filter_str else 'Нет'}")
            print(f"📄 Тип сканирования: {type_scan}")
            print(f"\n📊 СТАТИСТИКА ОБРАБОТКИ:")
            print(f"   Всего файлов:   {files_scanned}")
            print(f"   ➕ Добавлено:   {added}")
            print(f"   ✏️ Обновлено:   {updated}")
            print(f"   🗑 Удалено:     {deleted}")
            print(f"   📊 Изменений:   {added + updated + deleted}")


    def __printSessionChanges(self, session_id):
        cursor = self.__mainDataBase.getCursor()

        sql = '''SELECT
                    SC_ID, SC_FILE_NAME, SC_FILE_PATH,
                    SC_HASH_SUM, SC_OPERATION_TYPE, SC_TIME_CHANGE
                FROM scan_changes
                WHERE SC_SESSION_ID = ?
                ORDER BY SC_TIME_CHANGE'''

        cursor.execute(sql, (session_id,))
        changes = cursor.fetchall()

        if not changes:
            print("\n📭 В этой сессии не было изменений")
            return

        print(f"\n📝 СПИСОК ИЗМЕНЕНИЙ ({len(changes)} операций):")
        print("-" * 80)

                # Считаем операции по типам
        op_count = {'ADDED': 0, 'UPDATED': 0, 'DELETED': 0}
        op_emoji = {'ADDED': '➕', 'UPDATED': '✏️', 'DELETED': '🗑'}

        for change in changes:
            (sc_id, file_name, file_path, hash_sum, op_type, time_change) = change
            op_count[op_type] = op_count.get(op_type, 0) + 1

                    # Выводим только первые 20 изменений для читаемости
            if len(changes) <= 20 or sc_id <= 20:
                print(f"  {op_emoji.get(op_type, '❓')} {op_type}: {file_name}")
                print(f"     📁 {file_path}")
                print(f"     🕐 {time_change}")
                if op_type in ['ADDED', 'UPDATED']:
                    print(f"     🔑 Хэш: {hash_sum[:16]}...")
                    print()

        if len(changes) > 20:
            print(f"  ... и еще {len(changes) - 20} изменений")

        print(f"\n📊 ИТОГО ПО ОПЕРАЦИЯМ:")
        for op_type, count in op_count.items():
            print(f"   {op_emoji.get(op_type, '❓')} {op_type}: {count}")


    def showStatistic(self):
        cursor = self.__mainDataBase.getCursor()

        print(f"\n{'='*80}")
        print("📊 ОБЩАЯ СТАТИСТИКА БАЗЫ ДАННЫХ")
        print(f"{'='*80}")

                # Общее количество файлов
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]

                # Количество форматов
        cursor.execute("SELECT COUNT(*) FROM formats")
        total_formats = cursor.fetchone()[0]

                # Количество сессий
        cursor.execute("SELECT COUNT(*) FROM scan_sessions")
        total_sessions = cursor.fetchone()[0]

                # Общее количество изменений
        cursor.execute("SELECT COUNT(*) FROM scan_changes")
        total_changes = cursor.fetchone()[0]

        print(f"📄 Всего файлов:        {total_files}")
        print(f"📋 Всего форматов:      {total_formats}")
        print(f"🔄 Всего сессий:        {total_sessions}")
        print(f"📝 Всего изменений:     {total_changes}")

                # Статистика по операциям
        cursor.execute('''SELECT SC_OPERATION_TYPE, COUNT(*)
                                  FROM scan_changes
                                  GROUP BY SC_OPERATION_TYPE''')
        op_stats = cursor.fetchall()

        if op_stats:
            print(f"\n📊 Статистика операций:")
            op_emoji = {'ADDED': '➕', 'UPDATED': '✏️', 'DELETED': '🗑'}
            for op_type, count in op_stats:
                print(f"   {op_emoji.get(op_type, '❓')} {op_type}: {count}")

                # Самые активные сессии
        cursor.execute('''SELECT SS_ID, SS_PATH, SS_FILES_SCANNED,
                                         SS_CNT_ADDED + SS_CNT_UPDATED + SS_CNT_DELETED as total_changes
                                  FROM scan_sessions
                                  ORDER BY total_changes DESC
                                  LIMIT 5''')
        top_sessions = cursor.fetchall()

        if top_sessions:
            print(f"\n🔥 Самые активные сессии:")
            for ss_id, path, files, changes in top_sessions:
                print(f"   Сессия #{ss_id}: {changes} изменений, {files} файлов")
                print(f"   📁 {path[:60]}...")
