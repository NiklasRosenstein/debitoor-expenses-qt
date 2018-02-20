import sys
from Qt import QtWidgets
from .MainWindow import MainWindow

def main():
  global app  # Prevents QObject::startTimer: QTimer can only be used with threads started with QThread
  app = QtWidgets.QApplication(sys.argv)
  wnd = MainWindow()
  wnd.show()
  app.exec_()
