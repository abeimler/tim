#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication

from timmu.mainform import MainForm

app = QApplication(sys.argv)
w = MainForm()
w.show()
sys.exit(app.exec_())
