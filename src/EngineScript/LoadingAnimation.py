import time
import sys
from threading import Thread

class LoadingAnimation:
    def __init__(self, message="успешно", duration=0.3):
        self.__message = message
        self.__duration = duration
        self.__is_running = False
        self.__thread = None


    def __animate(self):
        dots = ['   ', '.  ', '.. ', '...']
        i = 0
        while self.__is_running:
            sys.stdout.write(f'\r{self.__message}{dots[i % len(dots)]}\n')
            sys.stdout.flush()
            time.sleep(self.__duration)
            i += 1


    """Запуск анимации в отдельном потоке"""
    def start(self):
        self.__is_running = True
        self.__thread = Thread(target=self.__animate)
        self.__thread.daemon = True
        self.__thread.start()


    """Остановка анимации"""
    def stop(self):
        self.__is_running = False
        if self.__thread:
            self.__thread.join()
        sys.stdout.write('\r' + ' ' * 50 + '\r')  # Очистка строки
