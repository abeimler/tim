import sys
import os
import subprocess

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from mainform import MainForm

def main():
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()