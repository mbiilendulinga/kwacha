CREATE DATABASE IF NOT EXISTS `kwacha_bank`;

USE `kwacha_bank`;

-- =========================================================
-- 1. ACCOUNT TYPES
-- =========================================================

CREATE TABLE IF NOT EXISTS account_types (
    account_type_id VARCHAR(10) PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    minimum_balance DECIMAL(15,2) DEFAULT 0,
    monthly_fee DECIMAL(15,2) DEFAULT 0,
    interest_rate DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. LOAN PRODUCTS
-- =========================================================

CREATE TABLE IF NOT EXISTS loan_products (
    loan_product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    loan_category VARCHAR(50) NOT NULL,
    minimum_amount DECIMAL(15,2) NOT NULL,
    maximum_amount DECIMAL(15,2) NOT NULL,
    base_interest_rate DECIMAL(5,2) NOT NULL,
    maximum_term_months INT NOT NULL,
    collateral_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 3. BRANCHES
-- =========================================================

CREATE TABLE IF NOT EXISTS branches (
    branch_id VARCHAR(10) PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    province VARCHAR(50) NOT NULL,
    district VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    branch_type VARCHAR(50),
    opening_date DATE,
    monthly_operating_cost DECIMAL(15,2)
);


-- =========================================================
-- 4. CUSTOMERS
-- =========================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    nationality VARCHAR(50),
    province VARCHAR(50),
    district VARCHAR(100),
    employment_status VARCHAR(50),
    occupation VARCHAR(100),
    employer_type VARCHAR(100),
    monthly_income DECIMAL(15,2),
    customer_since DATE NOT NULL,
    marital_status VARCHAR(30),
    dependents INT DEFAULT 0,
    risk_rating VARCHAR(20),
    kyc_status VARCHAR(30),
    customer_segment VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 5. EMPLOYEES
-- =========================================================

CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    branch_id VARCHAR(10),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    job_title VARCHAR(100),
    department VARCHAR(100),
    employment_date DATE,
    salary DECIMAL(15,2),
    employment_status VARCHAR(30),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


-- =========================================================
-- 6. ACCOUNTS
-- =========================================================

CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    account_type_id VARCHAR(10) NOT NULL,
    branch_id VARCHAR(10) NOT NULL,
    account_number VARCHAR(30) UNIQUE NOT NULL,
    currency VARCHAR(10) DEFAULT 'ZMW',
    open_date DATE NOT NULL,
    close_date DATE NULL,
    current_balance DECIMAL(15,2) DEFAULT 0,
    available_balance DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(30) DEFAULT 'Active',
    interest_rate DECIMAL(5,2) DEFAULT 0,
    overdraft_limit DECIMAL(15,2) DEFAULT 0,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (account_type_id)
        REFERENCES account_types(account_type_id),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


-- =========================================================
-- 7. CARDS
-- =========================================================

CREATE TABLE IF NOT EXISTS cards (
    card_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    card_type VARCHAR(30),
    issue_date DATE,
    expiry_date DATE,
    status VARCHAR(30),
    daily_limit DECIMAL(15,2),
    international_enabled BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
);


-- =========================================================
-- 8. TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(30) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    transaction_date DATETIME NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'ZMW',
    channel VARCHAR(50),
    branch_id VARCHAR(10),
    merchant_id VARCHAR(50),
    reference_number VARCHAR(50),
    balance_before DECIMAL(15,2),
    balance_after DECIMAL(15,2),
    transaction_status VARCHAR(30),
    location VARCHAR(100),
    is_reversal BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


-- =========================================================
-- 9. ATM TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS atm_transactions (
    atm_transaction_id VARCHAR(30) PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    atm_id VARCHAR(20) NOT NULL,
    card_id VARCHAR(20),
    transaction_datetime DATETIME NOT NULL,
    transaction_type VARCHAR(50),
    amount DECIMAL(15,2),
    location VARCHAR(100),
    available_cash_before DECIMAL(15,2),
    available_cash_after DECIMAL(15,2),
    status VARCHAR(30),

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (card_id)
        REFERENCES cards(card_id)
);


-- =========================================================
-- 10. DIGITAL TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS digital_transactions (
    digital_transaction_id VARCHAR(30) PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    channel VARCHAR(50),
    device_type VARCHAR(50),
    operating_system VARCHAR(50),
    ip_country VARCHAR(50),
    login_location VARCHAR(100),
    transaction_type VARCHAR(50),
    amount DECIMAL(15,2),
    transaction_datetime DATETIME,
    device_id VARCHAR(100),
    status VARCHAR(30),

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- =========================================================
-- 11. LOANS
-- =========================================================

CREATE TABLE IF NOT EXISTS loans (
    loan_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    loan_product_id VARCHAR(10) NOT NULL,
    branch_id VARCHAR(10) NOT NULL,
    application_date DATE,
    approval_date DATE,
    disbursement_date DATE,
    loan_amount DECIMAL(15,2),
    interest_rate DECIMAL(5,2),
    term_months INT,
    monthly_installment DECIMAL(15,2),
    outstanding_balance DECIMAL(15,2),
    loan_status VARCHAR(30),
    credit_score INT,
    collateral_value DECIMAL(15,2),
    default_probability DECIMAL(6,4),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (loan_product_id)
        REFERENCES loan_products(loan_product_id),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


-- =========================================================
-- 12. LOAN PAYMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS loan_payments (
    payment_id VARCHAR(30) PRIMARY KEY,
    loan_id VARCHAR(30) NOT NULL,
    payment_date DATE NOT NULL,
    amount_due DECIMAL(15,2),
    amount_paid DECIMAL(15,2),
    principal_paid DECIMAL(15,2),
    interest_paid DECIMAL(15,2),
    days_late INT DEFAULT 0,
    payment_status VARCHAR(30),
    payment_method VARCHAR(50),

    FOREIGN KEY (loan_id)
        REFERENCES loans(loan_id)
);


-- =========================================================
-- 13. FRAUD ALERTS
-- =========================================================

CREATE TABLE IF NOT EXISTS fraud_alerts (
    alert_id VARCHAR(30) PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    alert_datetime DATETIME,
    alert_type VARCHAR(100),
    risk_score DECIMAL(5,2),
    severity VARCHAR(20),
    detection_method VARCHAR(50),
    investigation_status VARCHAR(50),
    confirmed_fraud BOOLEAN DEFAULT FALSE,
    resolution_date DATETIME NULL,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- =========================================================
-- 14. CUSTOMER INTERACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS customer_interactions (
    interaction_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    interaction_date DATETIME NOT NULL,
    interaction_type VARCHAR(50),
    channel VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    resolution_status VARCHAR(50),
    resolution_time_hours DECIMAL(10,2),
    satisfaction_score INT,
    employee_id VARCHAR(20),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
);


-- =========================================================
-- 15. MONTHLY CUSTOMER METRICS
-- =========================================================

CREATE TABLE IF NOT EXISTS monthly_customer_metrics (
    customer_id VARCHAR(20) NOT NULL,
    month DATE NOT NULL,
    ending_balance DECIMAL(15,2),
    total_deposits DECIMAL(15,2),
    total_withdrawals DECIMAL(15,2),
    transaction_count INT,
    digital_transaction_count INT,
    atm_transaction_count INT,
    loan_payment_amount DECIMAL(15,2),
    average_transaction DECIMAL(15,2),
    largest_transaction DECIMAL(15,2),
    fraud_alert_count INT,
    customer_complaints INT,
    active_days INT,

    PRIMARY KEY (customer_id, month),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- =========================================================
-- 16. MERCHANTS
-- =========================================================

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id VARCHAR(50) PRIMARY KEY,
    merchant_name VARCHAR(150) NOT NULL,
    merchant_category VARCHAR(100),
    province VARCHAR(50),
    district VARCHAR(100),
    city VARCHAR(100),
    business_type VARCHAR(100)
);


-- =========================================================
-- 17. SALARY PAYMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS salary_payments (
    salary_payment_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    employer_name VARCHAR(150),
    payment_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    salary_month DATE,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX idx_transactions_account
ON transactions(account_id);

CREATE INDEX idx_transactions_customer
ON transactions(customer_id);

CREATE INDEX idx_transactions_date
ON transactions(transaction_date);

CREATE INDEX idx_transactions_type
ON transactions(transaction_type);

CREATE INDEX idx_transactions_channel
ON transactions(channel);

CREATE INDEX idx_loans_customer
ON loans(customer_id);

CREATE INDEX idx_loans_status
ON loans(loan_status);

CREATE INDEX idx_loan_payments_loan
ON loan_payments(loan_id);

CREATE INDEX idx_loan_payments_date
ON loan_payments(payment_date);

CREATE INDEX idx_fraud_customer
ON fraud_alerts(customer_id);

CREATE INDEX idx_fraud_date
ON fraud_alerts(alert_datetime);

CREATE INDEX idx_salary_customer
ON salary_payments(customer_id);

CREATE INDEX idx_salary_date
ON salary_payments(payment_date);