from dal import * # type: ignore

def create_account(username, email, password):
    new_account = BankAccount(username=username, email=email, password=password)
    add_account(new_account)
    return new_account

def list_accounts():
    return list_all_accounts()

def search_account(account_id):
    return search_account_by_id(account_id)

def deposit_amount(account_id, amount):
    account = search_account(account_id)
    if account:
        deposit(account, amount)
        return account
    else:
        return None

def withdraw_amount(account_id, amount):
    account = search_account(account_id)
    if account:
        withdraw(account, amount)
        return account
    else:
        return None

def transfer_amount(from_account_id, to_account_id, amount):
    from_account = search_account(from_account_id)
    to_account = search_account(to_account_id)
    if from_account and to_account:
        transfer(from_account, to_account, amount)
        return (from_account, to_account)
    else:
        return None

def delete_account(account_id):
    account = search_account(account_id)
    if account:
        delete_account(account)
        return account
    else:
        return None
