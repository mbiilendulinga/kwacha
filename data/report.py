import mysql.connector
from mysql.connector import Error

DB_NAME = "kwacha_bank"
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"


def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DB_NAME
    )


def run(cursor, title, sql):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [c[0] for c in cursor.description]
        print(" | ".join(cols))
        print("-" * 70)
        for r in rows:
            print(" | ".join("" if v is None else str(v) for v in r))
        if not rows:
            print("(no data)")
    except Error as e:
        print(f"ERROR: {e}")


def main():
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()

        # =========================================================
        # PAGE 1 – EXECUTIVE SUMMARY
        # =========================================================
        run(cur, "P1.1 CUSTOMER GROWTH (YEARLY)", """
            SELECT YEAR(customer_since) AS yr,
                   COUNT(*) AS new_customers
            FROM customers
            GROUP BY yr
            ORDER BY yr
        """)

        run(cur, "P1.2 TRANSACTION CHANNELS (COUNT + VALUE)", """
            SELECT channel,
                   COUNT(*) AS txn_count,
                   SUM(amount) AS total_value
            FROM transactions
            GROUP BY channel
            ORDER BY txn_count DESC
        """)

        run(cur, "P1.3 LOAN PORTFOLIO SUMMARY", """
            SELECT
                COUNT(*) AS total_loans,
                SUM(loan_amount) AS total_disbursed,
                SUM(outstanding_balance) AS total_outstanding,
                AVG(interest_rate) AS avg_interest_rate,
                AVG(default_probability) AS avg_default_prob
            FROM loans
        """)

        # =========================================================
        # PAGE 2 – CUSTOMER ANALYTICS
        # =========================================================
        run(cur, "P2.1 CUSTOMERS BY SEGMENT", """
            SELECT customer_segment, COUNT(*) AS customers
            FROM customers GROUP BY customer_segment ORDER BY customers DESC
        """)

        run(cur, "P2.2 CUSTOMER ACQUISITION (YEARLY)", """
            SELECT YEAR(customer_since) AS yr, COUNT(*) AS new_customers
            FROM customers GROUP BY yr ORDER BY yr
        """)

        run(cur, "P2.3 CUSTOMERS BY PROVINCE", """
            SELECT province, COUNT(*) AS customers
            FROM customers GROUP BY province ORDER BY customers DESC
        """)

        run(cur, "P2.4 CUSTOMERS BY EMPLOYMENT STATUS", """
            SELECT employment_status, COUNT(*) AS customers
            FROM customers GROUP BY employment_status ORDER BY customers DESC
        """)

        run(cur, "P2.5 CUSTOMERS BY RISK RATING", """
            SELECT risk_rating, COUNT(*) AS customers
            FROM customers GROUP BY risk_rating ORDER BY customers DESC
        """)

        run(cur, "P2.6 CUSTOMERS BY GENDER", """
            SELECT gender, COUNT(*) AS customers
            FROM customers GROUP BY gender ORDER BY customers DESC
        """)

        # =========================================================
        # PAGE 3 – DEPOSITS & ACCOUNTS
        # =========================================================
        run(cur, "P3.1 DEPOSITS BY ACCOUNT TYPE", """
            SELECT at.account_name,
                   COUNT(a.account_id) AS accounts,
                   SUM(a.current_balance) AS total_balance
            FROM accounts a
            JOIN account_types at ON a.account_type_id = at.account_type_id
            GROUP BY at.account_name
            ORDER BY total_balance DESC
        """)

        run(cur, "P3.2 NUMBER OF ACCOUNTS BY TYPE", """
            SELECT at.account_name, COUNT(*) AS accounts
            FROM accounts a
            JOIN account_types at ON a.account_type_id = at.account_type_id
            GROUP BY at.account_name ORDER BY accounts DESC
        """)

        run(cur, "P3.3 DEPOSITS BY BRANCH", """
            SELECT b.branch_name,
                   COUNT(a.account_id) AS accounts,
                   SUM(a.current_balance) AS total_balance
            FROM accounts a
            JOIN branches b ON a.branch_id = b.branch_id
            GROUP BY b.branch_name
            ORDER BY total_balance DESC
        """)

        run(cur, "P3.4 ACCOUNT OPENING TRENDS (YEARLY)", """
            SELECT YEAR(open_date) AS yr, COUNT(*) AS accounts_opened
            FROM accounts GROUP BY yr ORDER BY yr
        """)

        run(cur, "P3.5 CURRENT VS AVAILABLE BALANCES", """
            SELECT
                SUM(current_balance) AS total_current,
                SUM(available_balance) AS total_available,
                SUM(current_balance - available_balance) AS difference
            FROM accounts
        """)

        # =========================================================
        # PAGE 5 – TRANSACTIONS & DIGITAL BANKING
        # =========================================================
        run(cur, "P5.1 TRANSACTION VOLUME OVER TIME (YEARLY)", """
            SELECT YEAR(transaction_date) AS yr,
                   COUNT(*) AS txn_count,
                   SUM(amount) AS total_value
            FROM transactions GROUP BY yr ORDER BY yr
        """)

        run(cur, "P5.2 SHARE OF TRANSACTION TYPE", """
            SELECT transaction_type,
                   COUNT(*) AS txn_count,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 2) AS pct
            FROM transactions
            GROUP BY transaction_type ORDER BY txn_count DESC
        """)

        run(cur, "P5.3 TRANSACTION METHODS", """
            SELECT channel,
                   COUNT(*) AS txn_count,
                   SUM(amount) AS total_value
            FROM transactions GROUP BY channel ORDER BY txn_count DESC
        """)

        run(cur, "P5.4 TRANSACTION VALUE BY CHANNEL", """
            SELECT channel, SUM(amount) AS total_value
            FROM transactions GROUP BY channel ORDER BY total_value DESC
        """)

        run(cur, "P5.5 TRANSACTIONS BY DEVICE TYPE", """
            SELECT device_type, COUNT(*) AS txn_count, SUM(amount) AS total_value
            FROM digital_transactions GROUP BY device_type ORDER BY txn_count DESC
        """)

        run(cur, "P5.6 MERCHANT CATEGORY", """
            SELECT m.merchant_category,
                   COUNT(t.transaction_id) AS txn_count,
                   SUM(t.amount) AS total_value
            FROM transactions t
            JOIN merchants m ON t.merchant_id = m.merchant_id
            GROUP BY m.merchant_category
            ORDER BY total_value DESC
        """)

        # =========================================================
        # PAGE 6 – LOANS & CREDIT RISK
        # =========================================================
        run(cur, "P6.1 LOAN PORTFOLIO BY CATEGORY", """
            SELECT lp.loan_category,
                   COUNT(*) AS loans,
                   SUM(l.loan_amount) AS disbursed,
                   SUM(l.outstanding_balance) AS outstanding
            FROM loans l
            JOIN loan_products lp ON l.loan_product_id = lp.loan_product_id
            GROUP BY lp.loan_category ORDER BY disbursed DESC
        """)

        run(cur, "P6.2 LOAN STATUS", """
            SELECT loan_status, COUNT(*) AS loans, SUM(outstanding_balance) AS outstanding
            FROM loans GROUP BY loan_status ORDER BY loans DESC
        """)

        run(cur, "P6.3 LOAN PAYMENT STATUS", """
            SELECT payment_status, COUNT(*) AS payments, SUM(amount_paid) AS total_paid
            FROM loan_payments GROUP BY payment_status ORDER BY payments DESC
        """)

        run(cur, "P6.4 LOAN DISBURSEMENTS (YEARLY)", """
            SELECT YEAR(disbursement_date) AS yr,
                   COUNT(*) AS loans,
                   SUM(loan_amount) AS disbursed
            FROM loans
            WHERE disbursement_date IS NOT NULL
            GROUP BY yr ORDER BY yr
        """)

        run(cur, "P6.5 CREDIT SCORE & DEFAULT PROBABILITY", """
            SELECT
                AVG(credit_score) AS avg_credit_score,
                MIN(credit_score) AS min_credit_score,
                MAX(credit_score) AS max_credit_score,
                AVG(default_probability) AS avg_default_prob,
                MIN(default_probability) AS min_default_prob,
                MAX(default_probability) AS max_default_prob
            FROM loans
        """)

        run(cur, "P6.6 OUTSTANDING LOANS BY PRODUCT", """
            SELECT lp.product_name,
                   COUNT(*) AS loans,
                   SUM(l.outstanding_balance) AS outstanding
            FROM loans l
            JOIN loan_products lp ON l.loan_product_id = lp.loan_product_id
            GROUP BY lp.product_name ORDER BY outstanding DESC
        """)

        # =========================================================
        # PAGE 7 – FRAUD & RISK
        # =========================================================
        run(cur, "P7.1 FRAUD ALERTS OVER TIME (YEARLY)", """
            SELECT YEAR(alert_datetime) AS yr, COUNT(*) AS alerts
            FROM fraud_alerts GROUP BY yr ORDER BY yr
        """)

        run(cur, "P7.2 FRAUD SEVERITY", """
            SELECT severity, COUNT(*) AS alerts
            FROM fraud_alerts GROUP BY severity ORDER BY alerts DESC
        """)

        run(cur, "P7.3 FRAUD BY PROVINCE", """
            SELECT c.province, COUNT(*) AS alerts
            FROM fraud_alerts f
            JOIN customers c ON f.customer_id = c.customer_id
            GROUP BY c.province ORDER BY alerts DESC
        """)

        run(cur, "P7.4 FRAUD BY ALERT TYPE", """
            SELECT alert_type, COUNT(*) AS alerts
            FROM fraud_alerts GROUP BY alert_type ORDER BY alerts DESC
        """)

        run(cur, "P7.5 FRAUD DETECTION METHOD", """
            SELECT detection_method, COUNT(*) AS alerts
            FROM fraud_alerts GROUP BY detection_method ORDER BY alerts DESC
        """)

        run(cur, "P7.6 FRAUD INVESTIGATION STATUS", """
            SELECT investigation_status,
                   COUNT(*) AS alerts,
                   SUM(confirmed_fraud) AS confirmed
            FROM fraud_alerts GROUP BY investigation_status ORDER BY alerts DESC
        """)

        # =========================================================
        # PAGE 8 – BRANCH PERFORMANCE
        # =========================================================
        run(cur, "P8.1 DEPOSITS BY BRANCH", """
            SELECT b.branch_name, SUM(a.current_balance) AS deposits
            FROM accounts a JOIN branches b ON a.branch_id = b.branch_id
            GROUP BY b.branch_name ORDER BY deposits DESC
        """)

        run(cur, "P8.2 OUTSTANDING LOANS BY BRANCH", """
            SELECT b.branch_name, SUM(l.outstanding_balance) AS outstanding
            FROM loans l JOIN branches b ON l.branch_id = b.branch_id
            GROUP BY b.branch_name ORDER BY outstanding DESC
        """)

        run(cur, "P8.3 EMPLOYEES BY BRANCH", """
            SELECT b.branch_name, COUNT(e.employee_id) AS employees
            FROM branches b LEFT JOIN employees e ON b.branch_id = e.branch_id
            GROUP BY b.branch_name ORDER BY employees DESC
        """)

        run(cur, "P8.4 CUSTOMERS BY BRANCH", """
            SELECT b.branch_name, COUNT(DISTINCT a.customer_id) AS customers
            FROM accounts a JOIN branches b ON a.branch_id = b.branch_id
            GROUP BY b.branch_name ORDER BY customers DESC
        """)

        run(cur, "P8.5 BRANCH EFFICIENCY & OPERATING COST", """
            SELECT b.branch_name,
                   b.monthly_operating_cost,
                   COALESCE(SUM(a.current_balance),0) AS deposits,
                   ROUND(COALESCE(SUM(a.current_balance),0) / NULLIF(b.monthly_operating_cost,0), 2) AS efficiency_ratio
            FROM branches b
            LEFT JOIN accounts a ON b.branch_id = a.branch_id
            GROUP BY b.branch_name, b.monthly_operating_cost
            ORDER BY efficiency_ratio DESC
        """)

        print("\n\nDONE. Copy all output above and paste it back.\n")

    except Error as e:
        print(f"MySQL Error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()