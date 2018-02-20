
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
    self.account.currentIndexChanged.connect(self.updatePaymentsList)
    hbar.addWidget(self.account)

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

  def updatePaymentsList(self):
    account = self.getAccount()
    self.payments.setAccount(account)
