import SQLscripts.database as db
from datetime import datetime
import os

class HistoryManager:
    def __init__(self, database):
        self.__mainDatabase = database
        self.__connect = self.__mainDatabase.getConnect()
        self.__cursor = self.__mainDatabase.getCursor()
        self.__currentSessionId = None

    def createSession(self, startTime, typeScan, pathScan, filter, cntFiles, cntAdded, cntUpdated, cntDeleted, status="COMPLETED"):
        if filter == "" or filter is None:
            filter = "Отсутствует"

        endTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sqlFormatText = '''INSERT INTO scan_sessions
        (SS_START_TIME, SS_END_TIME, SS_TYPE_SCAN, SS_PATH, SS_FILTER,
         SS_FILES_SCANNED, SS_CNT_ADDED, SS_CNT_UPDATED, SS_CNT_DELETED, SS_STATUS)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        self.__cursor.execute(sqlFormatText, (
            startTime, endTime, typeScan, pathScan, filter,
            cntFiles, cntAdded, cntUpdated, cntDeleted, status
        ))

        self.__connect.commit()

        self.__currentSessionId = self.__cursor.lastrowid
        return self.__currentSessionId

    def addChangeRecord(self, fileName, filePath, fileHash, operationType, timeChange=None):
        """
        Добавляет запись об изменении файла
        operationType: 'ADDED', 'UPDATED', 'DELETED'
        """
        if self.__currentSessionId is None:
            raise Exception("No active session. Create session first.")

        if timeChange is None:
            timeChange = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sqlFormatText = '''INSERT INTO scan_changes
        (SC_SESSION_ID, SC_FILE_NAME, SC_FILE_PATH, SC_HASH_SUM, SC_OPERATION_TYPE, SC_TIME_CHANGE)
        VALUES (?, ?, ?, ?, ?, ?)
        '''

        self.__cursor.execute(sqlFormatText, (
            self.__currentSessionId, fileName, filePath, fileHash, operationType, timeChange
        ))

        self.__connect.commit()

    def getCurrentSessionId(self):
        return self.__currentSessionId
