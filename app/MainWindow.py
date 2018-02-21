
from Qt import QtCore, QtWidgets
from . import api
from .PaymentsView import PaymentsView


class MainWindow(QtWidgets.QWidget):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setWindowTitle("Debitoor Expenses")
    mainLayout = QtWidgets.QVBoxLayout()
    self.setLayout(mainLayout)

    hbar = QtWidgets.QHBoxLayout()
    mainLayout.addLayout(hbar)
    hbar.addWidget(QtWidgets.QLabel('Account:'))
    self.account = QtWidgets.QComboBox()
    self.account.currentIndexChanged.connect(lambda: self.payments.setAccount(self.getAccount()))
    hbar.addWidget(self.account)

    hbar = QtWidgets.QHBoxLayout()
    hbar.addWidget(QtWidgets.QLabel('Search:'))
    self.searchText = QtWidgets.QLineEdit()
    self.searchText.returnPressed.connect(lambda: self.searchButton.clicked.emit())
    self.searchButton = QtWidgets.QPushButton('Go')
    self.searchButton.clicked.connect(lambda: self.payments.setSearchString(self.searchText.text()))
    hbar.addWidget(self.searchText)
    hbar.addWidget(self.searchButton)
    mainLayout.addLayout(hbar)

    hbar = QtWidgets.QHBoxLayout()
    mainLayout.addLayout(hbar)
    self.payments = PaymentsView()
    hbar.addWidget(self.payments)

    self.initValues()

  def initValues(self):
    for account in api.paymentaccounts():
      self.account.addItem(account['accountName'])

  def getAccount(self):
    return api.paymentaccounts()[self.account.currentIndex()]
