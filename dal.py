import psycopg2
from models import BankAccount, Operation

# Connexion à la base de données PostgreSQL
def connect_db():
    return psycopg2.connect(
        dbname="your_db", user="your_user", password="your_password", host="localhost", port="5432"
    )

# Ajouter un compte bancaire
def add_account(account: BankAccount):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bank_accounts (username, balance, email, password, date_creation) VALUES (%s, %s, %s, %s, %s) RETURNING id", 
                   (account.username, account.balance, account.email, account.password, account.date_creation))
    account.id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

# Rechercher un compte bancaire par ID
def search_account_by_id(account_id: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bank_accounts WHERE id = %s", (account_id,))
    account_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if account_data:
        return BankAccount(*account_data)
    else:
        return None

# Lister tous les comptes bancaires
def list_all_accounts():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bank_accounts ORDER BY balance DESC")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return [BankAccount(*account) for account in accounts]

# Dépôt d'argent dans un compte
def deposit(account: BankAccount, amount: float):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE bank_accounts SET balance = balance + %s WHERE id = %s", (amount, account.id))
    conn.commit()
    cursor.close()
    conn.close()

# Retrait d'argent d'un compte
def withdraw(account: BankAccount, amount: float):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE bank_accounts SET balance = balance - %s WHERE id = %s", (amount, account.id))
    conn.commit()
    cursor.close()
    conn.close()

# Transfert d'argent entre comptes
def transfer(from_account: BankAccount, to_account: BankAccount, amount: float):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE bank_accounts SET balance = balance - %s WHERE id = %s", (amount, from_account.id))
    cursor.execute("UPDATE bank_accounts SET balance = balance + %s WHERE id = %s", (amount, to_account.id))
    conn.commit()
    cursor.close()
    conn.close()

# Supprimer un compte bancaire
# Suppression d'un compte bancaire
def delete_account(account_id: int):  # Ici on doit utiliser account_id
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bank_accounts WHERE id = %s", (account_id,))
    conn.commit()
    cursor.close()
    conn.close()

