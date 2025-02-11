CREATE TABLE bank_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    balance FLOAT DEFAULT 0,
    email VARCHAR(100),
    password VARCHAR(100),
    date_creation TIMESTAMP DEFAULT NOW()
);
CREATE TABLE operations (
    id SERIAL PRIMARY KEY,
    account_id INT REFERENCES bank_accounts(id),
    type_operation VARCHAR(50),
    amount FLOAT,
    date_operation TIMESTAMP DEFAULT NOW()
);
