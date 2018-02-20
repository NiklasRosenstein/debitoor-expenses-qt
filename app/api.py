
import json
import os
import requests

with open(os.path.join(__file__ + '/../../config.json')) as fp:
  config = json.load(fp)

session = requests.Session()
session.headers['x-token'] = config['debitoorApiToken']


def request(method, endpoint, *args, **kwargs):
  r = session.request(method, 'https://api.debitoor.com' + endpoint, *args, **kwargs)
  r.raise_for_status()
  return r


def paymentaccounts():
  data = request('get', '/api/paymentaccounts/v1').json()
  return [PaymentAccount(x) for x in data]


class _Object:

  def __init__(self, data):
    self.data = data

  def __repr__(self):
    return '{}({!r})'.format(type(self).__name__, self.data)

  def __getitem__(self, key):
    return self.data[key]

  def to_json(self):
    return self.data

  def get(self, key, default=None):
    return self.data.get(key, default)


class PaymentAccount(_Object):

  def payments(self, limit=None, skip=None, from_date=None, to_date=None):
    params = {}
    if limit:
      params['limit'] = str(int(limit))
    if skip:
      params['skip'] = str(int(skip))
    if from_date:
      params['fromDate'] = from_date.strftime('%Y-%m-%d')
    if to_date:
      params['toDate'] = to_date.strftime('%Y-%m-%d')
    endpoint = '/api/paymentaccounts/{}/payments/v1'.format(self['id'])
    data = request('get', endpoint, params=params).json()
    return [Payment(x) for x in data]

  def transactions(self, from_amount=None, to_amount=None, matched=True,
      unmatched=True, private=True, search=None, limit=None, skip=None,
      from_date=None, to_date=None):
    params = {}
    if from_amount:
      params['fromAcount'] = str(float(fromAcount))
    if to_amount:
      params['toAmount'] = str(float(toAmount))
    if matched:
      params['matched'] = 'true'
    if unmatched:
      params['unmatched'] = 'true'
    if private:
      params['private'] = 'true'
    if search:
      params['search'] = str(search)
    if limit:
      params['limit'] = str(int(limit))
    if skip:
      params['skip'] = str(int(skip))
    if from_date:
      params['fromDate'] = from_date.strftime('%Y-%m-%d')
    if to_date:
      params['toDate'] = to_date.strftime('%Y-%m-%d')
    endpoint = '/api/paymentaccounts/{}/transactions/v1'.format(self['id'])
    data = request('get', endpoint, params=params).json()
    return [Transaction(x) for x in data]


class Payment(_Object):

  def delete(self):
    endpoint = '/api/payments/{}/v1'.format(self['id'])
    return request('delete', endpoint).json()

  @staticmethod
  def create_private(account_id, transaction_id, date, currency, amount):
    """
    Creates a private payment for a transaction. Should not be used if the
    transaction already has one type of payment assigned.

    Note: This is undocumented API.
    """

    data = {
      'paymentAccountId': account_id,
      'paymentTransactionId': transaction_id,
      'paymentDate': date,
      'currency': currency,
      'amount': amount
    }
    endpoint = '/api/v1.0/banktransactions/payments/private'
    return request('post', endpoint, json=data).json()


class Transaction(_Object):

  def __init__(self, data):
    data.setdefault('payments', {})
    super().__init__(data)

  def invoices(self):
    return [Payment(x) for x in self['payments'].get('invoices', [])]

  def credit_notes(self):
    return [Payment(x) for x in self['payments'].get('creditNotes', [])]

  def income(self):
    return [Payment(x) for x in self['payments'].get('income', [])]

  def expense(self):
    return [Payment(x) for x in self['payments'].get('expense', [])]

  def private(self):
    return [Payment(x) for x in self['payments'].get('private', [])]

  def transfer(self):
    return [Payment(x) for x in self['payments'].get('transfer', [])]

  def has_invoices(self):
    return 'invoices' in self['payments']

  def has_credit_notes(self):
    return 'creditNotes' in self['payments']

  def has_income(self):
    return 'income' in self['payments']

  def has_expense(self):
    return 'expense' in self['payments']

  def has_private(self):
    return 'private' in self['payments']

  def has_transfer(self):
    return 'transfer' in self['payments']

  def all(self):
    yield from self.invoices()
    yield from self.credit_notes()
    yield from self.income()
    yield from self.expense()
    yield from self.private()
    yield from self.transfer()

  def types(self):
    result = []
    if self.has_invoices():
      result.append('invoices')
    if self.has_credit_notes():
      result.append('credit_notes')
    if self.has_income():
      result.append('income')
    if self.has_expense():
      result.append('expense')
    if self.has_private():
      result.append('private')
    if self.has_transfer():
      result.append('transfer')
    return result

  def create_private(self):
    types = self.types()
    if self.types():
      raise ValueError('Transaction is already marked {}'
        .format(','.join(types)))
    # TODO: Use current date maybe?
    return Payment.create_private(self['accountId'], self['id'], self['date'],
      self['currency'], self['amount'])

  def update(self):
    self.data = self.get_transaction(self['id']).data

  @staticmethod
  def get_transaction(transaction_id):
    endpoint = '/api/paymentaccounts/transactions/{}/v1'.format(transaction_id)
    return Transaction(request('get', endpoint).json())
