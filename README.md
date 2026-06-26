# File Indexer & Comparator

Инструмент для индексации файлов в базе данных SQLite и сравнения директорий.

## Содержание

- Описание
- Аргументы командной строки
- Как это работает
- Установка
- Примеры использования
- Структура проекта

## Описание

File Indexer & Comparator — это утилита для:

- Индексации файлов в SQLite базе данных с хешированием содержимого
- Сравнения директорий для поиска изменений, переименований и удалений
- Создания резервных копий базы данных
- Фильтрации файлов по расширению

## Аргументы командной строки

### -d, --dir - Путь к рабочей директории

Что делает: Указывает директорию для сканирования и индексации

Использование:
python TerminalApp.py -d /path/to/directory
python TerminalApp.py --dir /path/to/directory

Пример:
python TerminalApp.py -d "C:/Users/User/Documents"

### -f, --filter - Фильтр по расширению

Что делает: Ограничивает сканирование файлами с указанным расширением

Использование:
python TerminalApp.py -d /path -f .txt
python TerminalApp.py --dir /path --filter .py

Пример:
python TerminalApp.py -d ./my_folder -f .txt
python TerminalApp.py -d ./project -f .py

### -c, --compare - Сравнение директорий

Что делает: Сравнивает две директории и показывает различия

Использование:
python TerminalApp.py -c /path/first /path/second
python TerminalApp.py --compare /path/first /path/second

Пример:
python TerminalApp.py -c ./source ./backup

Результат сравнения:
- [Изменен] - файл с одинаковым именем, но разным содержимым
- [Переименован] - файл с одинаковым содержимым, но разным именем
- [Удален] - файл, который есть в первой директории, но отсутствует во второй

### -b, --backup - Создание бэкапа базы данных

Что делает: Создает резервную копию базы данных в указанную директорию

Использование:
python TerminalApp.py -b /path/to/backup/folder
python TerminalApp.py --backup /path/to/backup/folder

Пример:
python TerminalApp.py -b ./backups
Создаст файл: backup_indexer_2026-06-26_15-30-45.db

### -i, -info - Информация о настройках

Что делает: Показывает текущие настройки программы

Использование:
python TerminalApp.py -i
python TerminalApp.py --info

Пример вывода:
{
    "countStarts": 24,
    "batchSize": 500
}

## Как это работает

### Процесс сканирования и индексации

Когда вы запускаете программу с аргументом -d, происходит следующее:

1. Чтение файлов
   - Рекурсивный обход указанной директории
   - Сбор всех файлов (или только с фильтром)

2. Создание объектов файлов
   - Получение информации о файле (имя, путь, размер)
   - Вычисление SHA-256 хеша содержимого
   - Создание объектов FileClass

3. Проверка в базе данных
   - Разбивка на batches (пакеты) по 500 файлов
   - Проверка каждого хеша в базе данных
   - Отбор только новых файлов

4. Добавление в базу данных
   - Получение ID формата файла (.txt, .py, .jpg и т.д.)
   - Сохранение информации о файле
   - Удаление дубликатов

### База данных

База данных SQLite содержит две основные таблицы:

Таблица formats (форматы файлов):
CREATE TABLE formats (
    F_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    F_NAME TEXT NOT NULL,
    F_ISBINARY BOOLEAN
);

Таблица files (файлы):
CREATE TABLE files (
    C_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    C_FILE_NAME TEXT NOT NULL,
    C_FULL_NAME TEXT NOT NULL,
    C_CHANGE_DATE DATETIME NOT NULL,
    C_CREATE_DATE DATETIME NOT NULL,
    C_FORMAT_ID INTEGER,
    C_HASH_SUM VARCHAR(64) NOT NULL,
    FOREIGN KEY (C_FORMAT_ID) REFERENCES formats(F_ID)
);

### Конфигурация

Программа создает файл config.json со следующими настройками:

{
    "countStarts": 24,
    "batchSize": 500
}

### Оптимизация производительности

- Пакетная обработка: Файлы обрабатываются пачками по 500 штук
- Индикация загрузки: Анимация во время длительных операций
- SHA-256 хеширование: Для быстрого сравнения содержимого

## Установка

1. Клонируйте репозиторий:
git clone <repository-url>
cd file-indexer

2. Установите зависимости (если есть):
pip install -r requirements.txt

3. Запустите программу:
python TerminalApp.py

## Примеры использования

### Основные сценарии

1. Индексация всех файлов в папке:
python TerminalApp.py -d ./documents

2. Индексация только Python файлов:
python TerminalApp.py -d ./project -f .py

3. Сравнение двух папок:
python TerminalApp.py -c ./backup ./current

4. Создание бэкапа базы:
python TerminalApp.py -b ./backups

5. Комбинирование команд:
python TerminalApp.py -d ./folder -f .txt -b ./backups

### Типичный рабочий процесс

Шаг 1: Индексация основных файлов
python TerminalApp.py -d ./source -f .txt

Шаг 2: Добавление новых файлов
python TerminalApp.py -d ./source/new_files

Шаг 3: Создание бэкапа перед изменениями
python TerminalApp.py -b ./backups

Шаг 4: Сравнение с другой директорией
python TerminalApp.py -c ./source ./modified

## Структура проекта

project/
├── TerminalApp.py
├── EngineScript/
│   ├── __init__.py
│   ├── EngineScript.py
│   ├── FileClass.py
│   └── LoadingAnimation.py
├── SQLscripts/
│   └── database.py
├── config.json
└── indexer.db

## Технические детали

- Python 3.8+
- SQLite3 - встроенная БД
- SHA-256 - хеширование файлов
- Поддержка больших файлов - чтение по 8KB
- Кроссплатформенность - работает на Windows, Linux, MacOS

## Обработка ошибок

- Автоматическое создание config.json при отсутствии
- Проверка существования директорий перед операциями
- Обработка ошибок чтения файлов
- Автоматическое создание таблиц БД при первом запуске
