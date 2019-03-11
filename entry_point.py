#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from timmu.mainform import MainForm

app = QApplication(sys.argv)
w = MainForm()
w.show()
sys.exit(app.exec_())
