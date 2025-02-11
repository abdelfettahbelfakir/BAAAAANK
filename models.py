import psycopg2
from datetime import datetime

class BankAccount:
    def __init__(self, id=None, username=None, balance=0.0, email=None, password=None, date_creation=None):
        self.id = id
        self.username = username
        self.balance = balance
        self.email = email
        self.password = password
        self.date_creation = date_creation if date_creation else datetime.now()

class Operation:
    def __init__(self, id=None, account_id=None, type_operation=None, amount=0.0, date_operation=None):
        self.id = id
        self.account_id = account_id
        self.type_operation = type_operation
        self.amount = amount
        self.date_operation = date_operation if date_operation else datetime.now()
