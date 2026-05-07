import sys
import os
from PyQt5 import QtWidgets, uic, QtGui

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        
        # 1. АВТОМАТИЧНИЙ ПОШУК ШЛЯХУ
        # Отримуємо шлях до папки, де лежить цей файл (interface.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Приєднуємо назву файлу інтерфейсу
        ui_path = os.path.join(current_dir, 'interface.ui')
        
        # Завантажуємо інтерфейс
        try:
            uic.loadUi(ui_path, self)
        except FileNotFoundError:
            print(f"ПОМИЛКА: Файл не знайдено за шляхом: {ui_path}")
            return

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())