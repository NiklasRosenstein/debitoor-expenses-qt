
import json
import string
from Qt import QtCore, QtWidgets


def render_string(fmt, data):
  class Accessor(object):
    def __getitem__(self, key):
      result = data
      for part in key.split('.'):
        if not isinstance(result, dict) or part not in result:
          raise KeyError(key)
        result = result[part]
      return result
  class Template(string.Template):
    idpattern = r'(?-i:[_a-zA-Z][_a-zA-Z0-9\.]*)'
  return Template(fmt).safe_substitute(Accessor())


class PaymentsListModel(QtCore.QAbstractItemModel):

  COLUMNS = [
    ('Amount', None),
    ('Category', '${category}'),
    ('Date', '${date}'),
    ('Description', '${otherParty.name}, ${text}')
  ]

  def __init__(self, account, searchString):
    super().__init__()
    self.account = account
    self.searchString = searchString
    self.data = account.transactions(search=searchString)
    self.data.sort(key=lambda x: x['date'], reverse=True)

  def index(self, row, column, parent):
    return self.createIndex(row, column)

  def parent(self, index):
    return QtCore.QModelIndex()

  def columnCount(self, parent):
    return len(self.COLUMNS)

  def rowCount(self, parent):
    return len(self.data)

  def headerData(self, section, orientation, role):
    if orientation == QtCore.Qt.Horizontal:
      if role == QtCore.Qt.DisplayRole:
        return self.COLUMNS[section][0]
    else:
      return None

  def data(self, index, role):
    if role == QtCore.Qt.DisplayRole:
      colname, fmt = self.COLUMNS[index.column()]
      transaction = self.data[index.row()]
      if colname == 'Amount':
        return '%.2f %s' % (float(transaction['amount']), transaction['currency'])

      data = transaction.json()
      data['category'] = ', '.join(transaction.types())
      return render_string(fmt, data)
    return None


class PaymentsView(QtWidgets.QTableView):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._account = None
    self._searchString = None
    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.customContextMenuRequested.connect(self._onContextMenu)
    self.horizontalHeader().setStretchLastSection(True)

  def _onContextMenu(self, mouse_pos):
    transactions = list(self.selectedTransactions())
    menu = QtWidgets.QMenu(self)
    if any(x.has_private() for x in transactions):
      action = QtWidgets.QAction("Revert Private", self)
      action.triggered.connect(self._onUnmarkAsPrivate)
      menu.addAction(action)
    if any(not x.types() for x in transactions):
      action = QtWidgets.QAction("Make Private", self)
      action.triggered.connect(self._onMarkAsPrivate)
      menu.addAction(action)
    menu.addSeparator()
    action = QtWidgets.QAction("Dump Info", self)
    action.triggered.connect(self._onDumpInfo)
    menu.addAction(action)
    menu.exec_(self.mapToGlobal(mouse_pos))

  def _onMarkAsPrivate(self, checked):
    for transaction in self.selectedTransactions():
      if transaction.types(): continue  # can not be marked as private
      print('Creating private payment for transaction', transaction['id'])
      transaction.create_private()
      transaction.update()

  def _onUnmarkAsPrivate(self, checked):
    for transaction in self.selectedTransactions():
      for payment in transaction.private():
        print('Deleting payment', payment['id'])
        payment.delete()
      transaction.update()

  def _onDumpInfo(self, checked):
    for transaction in self.selectedTransactions():
      print(json.dumps(transaction.data, indent=2))
    print('-'*80)

  def selectedTransactions(self):
    selection = self.selectionModel()
    rows = set(x.row() for x in selection.selectedIndexes())
    model = self.model()
    for index in sorted(rows):
      yield model.data[index]

  def _updateModel(self):
    model = PaymentsListModel(self._account, self._searchString)
    self.setModel(model)

  def setAccount(self, account):
    self._account = account
    self._updateModel()

  def setSearchString(self, search):
    self._searchString = search
    self._updateModel()
