# Kwacha Bank | Banking Performance & Health

https://www.mbiile.com/projects/kwacha-bank/

A synthetic banking analytics project examining customer growth, deposits, transactions, lending, credit risk, fraud monitoring and branch performance within a Zambian retail banking environment.

## Project Overview

The objective of this project is to analyse a bank as an operating business rather than focusing on a single banking KPI.

The analysis brings together customer, account, deposit, transaction, loan, fraud and branch data to answer questions such as:

* How quickly is the customer base growing?
* Are account openings growing at the same rate as customers?
* Where are deposits concentrated?
* How has lending activity changed?
* What does the current loan status mix look like?
* How is customer risk distributed?
* What does transaction activity look like across channels?
* How large is the fraud-alert workload?
* How does branch activity differ across locations?

The project uses synthetic data and is intended for portfolio and analytical demonstration purposes.

## Key Results

### Customer Growth

Customer acquisition increased from 1,103 in 2021 to 1,335 in 2025, representing a 21.0% increase.

Growth slowed in 2025 to 3.3%, following increases of 10.1% in 2023 and 7.8% in 2024.

### Account Growth

Account openings increased from 847 in 2021 to 3,753 in 2025.

That represents a 343.1% increase, substantially faster than customer growth.

The dataset contains 15,426 accounts across 10,000 customers, or approximately 1.54 accounts per customer.

### Deposits

Current account balances total approximately K2.031 billion.

The five largest account categories account for 72.5% of total balances.

Salary and Basic Savings accounts together represent approximately 35.5% of balances.

### Lending

Cumulative loan disbursements total K290.9 million, with K90.7 million outstanding.

Annual loan disbursements increased from:

| Year | Loans | Disbursement |
| ---- | ----: | -----------: |
| 2023 |   925 |      K54.14m |
| 2024 | 1,145 |      K64.69m |
| 2025 | 1,974 |     K119.63m |

Disbursement value increased by 121.0% between 2023 and 2025.

### Risk

The customer risk profile is:

| Risk   | Customers | Share |
| ------ | --------: | ----: |
| Low    |     5,164 | 51.6% |
| Medium |     3,295 | 33.0% |
| High   |     1,541 | 15.4% |

### Fraud Monitoring

The reconciled fraud dataset contains 43,483 alerts.

Approximately 88.0% are classified as low severity, 10.9% as medium, 1.1% as high and 0.03% as critical.

## Data

The project contains several interconnected areas of banking data.

### Customers

10,000 customer records covering:

 Segment
 Province
 Employment
 Gender
 Risk classification
 Acquisition history

### Accounts

15,426 account records covering:

 Account type
 Opening date
 Balance
 Current balance
 Available balance

### Transactions

1,000,000 transaction records covering:

 Transaction type
 Transaction channel
 Transaction value
 Date
 Device information where available

### Loans

5,000 loan records covering:

 Loan category
 Loan product
 Status
 Disbursement
 Outstanding balance
 Interest rate
 Credit score
 Default probability
 Payment status

### Fraud

43,483 fraud-alert records covering:

 Alert type
 Severity
 Province
 Detection method
 Investigation status
 Confirmation status

### Branches

Branch-level information covering:

 Customers
 Employees
 Deposits
 Outstanding loans
 Monthly operating costs

## Technology Stack

Python

Used for synthetic data generation, database creation and analytical checks.

MySQL

Used as the relational database for the project.

SQL

Used for data extraction, aggregation, reconciliation and analysis.

Power BI

Used to build the interactive banking performance report.

DAX

Used for Power BI measures and dynamic calculations.

Django

Used to present the project as part of the portfolio website.

## Project Structure

```text
kwacha-bank/
│
├── dax/
│   └── measures.dax
│
├── data/
│   └── ...
│
├── insights/
│   └── insights.md
│
├── powerbi/
│   └── Kwacha_Bank.pbix
│
├── python/
│   ├── ...
│   └── report.py
│
├── screenshots/
│   └── ...
│
├── sql/
│   ├── ...
│   └── schema.sql
│
└── README.md
```

## Analytical Period

The project uses different periods depending on the dataset available.

| Area                 | Period           |
| -------------------- | ---------------- |
| Customer acquisition | 2021–2025        |
| Account openings     | 2021–2025        |
| Loan disbursements   | 2023–2025        |
| Transactions         | 2025–2026        |
| Fraud alerts         | 2025–2026        |
| Deposits             | Current snapshot |
| Branch balances      | Current snapshot |

The 2021–2025 period is therefore used for the main customer and account growth analysis rather than forcing incomplete transaction or fraud history into the same trend.

## Data Validation

Data validation was performed before the results were interpreted.

One notable reconciliation involved the fraud data.

The annual fraud totals are:

 2025: 17,113
 2026: 26,370
 Total: 43,483

The severity, province, detection-method and investigation-status breakdowns also reconcile to 43,483.

This prevents the report from using an incorrect total of 53,483.

## Important Limitations

This is a synthetic dataset, so the results should not be interpreted as the performance of an actual bank.

Some datasets have different time coverage. In particular, transactions and fraud only have 2025–2026 history in the current version.

Deposit and branch figures are snapshots rather than complete annual series.

Loan status records include rejected and approved loans, so the proportion of defaulted records is not a formal default rate.

The branch deposit-to-cost calculation is a project-specific comparison metric rather than a standard banking efficiency ratio.

Device information is available for only a subset of transaction records.

## Dashboard

The Power BI report examines:

1. Customer Overview
2. Customer Segments
3. Deposits and Accounts
4. Transactions
5. Lending and Credit Risk
6. Fraud Monitoring
7. Branch Performance

The report can be filtered by dimensions including year, province, branch, customer segment, account type, loan category, loan status and risk classification.

## Portfolio Project

The project is also available as an interactive project page:

https://www.mbiile.com/projects/kwacha-bank/

## Purpose

This project was built to demonstrate practical skills in:

 SQL
 Python
 Data modelling
 Data validation
 DAX
 Power BI
 Financial analysis
 Banking analytics
 Risk analysis
 Business intelligence
 Data storytelling
