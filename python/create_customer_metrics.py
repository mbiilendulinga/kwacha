import mysql.connector
from mysql.connector import Error
from decimal import Decimal
from datetime import date


# ============================================================
# KWACHA BANK
# MONTHLY CUSTOMER METRICS GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():

    try:

        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

    except Error as e:

        print(
            f"MySQL connection error: {e}"
        )

        return None


# ============================================================
# SAFE DECIMAL
# ============================================================

def decimal(value):

    if value is None:
        return Decimal("0.00")

    return Decimal(str(value))


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("MONTHLY CUSTOMER METRICS GENERATOR")
    print("=" * 70)

    print(
        "\nMetrics will be calculated from "
        "existing banking data."
    )

    print(
        "No artificial random metrics will be created."
    )

    print("\n")
    print("=" * 70)
    print("CONNECTING TO MYSQL")
    print("=" * 70)

    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor(dictionary=True)

    try:

        # ====================================================
        # DETERMINE DATE RANGE
        # ====================================================

        print("\nDetermining analysis period...")

        cursor.execute("""
            SELECT MIN(transaction_date) AS min_date,
                   MAX(transaction_date) AS max_date
            FROM transactions
        """)

        transaction_dates = cursor.fetchone()

        min_date = transaction_dates["min_date"]
        max_date = transaction_dates["max_date"]

        if min_date is None:

            print(
                "\nNo transactions found."
            )

            return

        start_month = date(
            min_date.year,
            min_date.month,
            1
        )

        end_month = date(
            max_date.year,
            max_date.month,
            1
        )

        print(
            f"Analysis period: "
            f"{start_month} → {end_month}"
        )

        # ====================================================
        # LOAD CUSTOMERS
        # ====================================================

        print("\nLoading customers...")

        cursor.execute("""
            SELECT
                customer_id,
                customer_since
            FROM customers
        """)

        customers = cursor.fetchall()

        print(
            f"Loaded {len(customers):,} customers."
        )

        # ====================================================
        # TRANSACTION AGGREGATES
        # ====================================================

        print("\nCalculating transaction metrics...")

        # Replaced DATE(YEAR(...), MONTH(...), 1) with DATE_FORMAT
        cursor.execute("""
            SELECT
                customer_id,
                DATE_FORMAT(transaction_date, '%Y-%m-01') AS month,
                SUM(
                    CASE
                        WHEN transaction_type IN (
                            'Deposit',
                            'Cash Deposit',
                            'Salary',
                            'Transfer In',
                            'Credit'
                        )
                        THEN amount
                        ELSE 0
                    END
                ) AS total_deposits,
                SUM(
                    CASE
                        WHEN transaction_type IN (
                            'Withdrawal',
                            'Cash Withdrawal',
                            'Transfer Out',
                            'Debit',
                            'Payment'
                        )
                        THEN amount
                        ELSE 0
                    END
                ) AS total_withdrawals,
                COUNT(*) AS transaction_count,
                AVG(amount) AS average_transaction,
                MAX(amount) AS largest_transaction,
                COUNT(
                    DISTINCT DATE(transaction_date)
                ) AS active_days
            FROM transactions
            GROUP BY
                customer_id,
                DATE_FORMAT(transaction_date, '%Y-%m-01')
        """)

        transaction_metrics = cursor.fetchall()

        transaction_map = {}

        for row in transaction_metrics:

            key = (
                row["customer_id"],
                row["month"]
            )

            transaction_map[key] = row

        print(
            f"Transaction metric groups: "
            f"{len(transaction_map):,}"
        )

        # ====================================================
        # DIGITAL TRANSACTIONS
        # ====================================================

        print(
            "\nCalculating digital transaction metrics..."
        )

        cursor.execute("""
            SELECT
                customer_id,
                DATE_FORMAT(transaction_datetime, '%Y-%m-01') AS month,
                COUNT(*) AS digital_count
            FROM digital_transactions
            GROUP BY
                customer_id,
                DATE_FORMAT(transaction_datetime, '%Y-%m-01')
        """)

        digital_rows = cursor.fetchall()

        digital_map = {}

        for row in digital_rows:

            digital_map[
                (
                    row["customer_id"],
                    row["month"]
                )
            ] = row["digital_count"]

        print(
            f"Digital metric groups: "
            f"{len(digital_map):,}"
        )

        # ====================================================
        # ATM TRANSACTIONS
        # ====================================================

        print(
            "\nCalculating ATM transaction metrics..."
        )

        cursor.execute("""
            SELECT
                t.customer_id,
                DATE_FORMAT(a.transaction_datetime, '%Y-%m-01') AS month,
                COUNT(*) AS atm_count
            FROM atm_transactions a
            INNER JOIN transactions t
                ON a.transaction_id = t.transaction_id
            GROUP BY
                t.customer_id,
                DATE_FORMAT(a.transaction_datetime, '%Y-%m-01')
        """)

        atm_rows = cursor.fetchall()

        atm_map = {}

        for row in atm_rows:

            atm_map[
                (
                    row["customer_id"],
                    row["month"]
                )
            ] = row["atm_count"]

        print(
            f"ATM metric groups: "
            f"{len(atm_map):,}"
        )

        # ====================================================
        # LOAN PAYMENTS
        # ====================================================

        print(
            "\nCalculating loan payment metrics..."
        )

        cursor.execute("""
            SELECT
                l.customer_id,
                DATE_FORMAT(p.payment_date, '%Y-%m-01') AS month,
                SUM(
                    COALESCE(
                        p.amount_paid,
                        0
                    )
                ) AS loan_payment_amount
            FROM loan_payments p
            INNER JOIN loans l
                ON p.loan_id = l.loan_id
            GROUP BY
                l.customer_id,
                DATE_FORMAT(p.payment_date, '%Y-%m-01')
        """)

        loan_rows = cursor.fetchall()

        loan_map = {}

        for row in loan_rows:

            loan_map[
                (
                    row["customer_id"],
                    row["month"]
                )
            ] = decimal(
                row["loan_payment_amount"]
            )

        print(
            f"Loan payment groups: "
            f"{len(loan_map):,}"
        )

        # ====================================================
        # FRAUD ALERTS
        # ====================================================

        print(
            "\nCalculating fraud alert metrics..."
        )

        cursor.execute("""
            SELECT
                customer_id,
                DATE_FORMAT(alert_datetime, '%Y-%m-01') AS month,
                COUNT(*) AS fraud_count
            FROM fraud_alerts
            GROUP BY
                customer_id,
                DATE_FORMAT(alert_datetime, '%Y-%m-01')
        """)

        fraud_rows = cursor.fetchall()

        fraud_map = {}

        for row in fraud_rows:

            fraud_map[
                (
                    row["customer_id"],
                    row["month"]
                )
            ] = row["fraud_count"]

        print(
            f"Fraud metric groups: "
            f"{len(fraud_map):,}"
        )

        # ====================================================
        # CUSTOMER COMPLAINTS
        # ====================================================

        print(
            "\nCalculating complaint metrics..."
        )

        cursor.execute("""
            SELECT
                customer_id,
                DATE_FORMAT(interaction_date, '%Y-%m-01') AS month,
                COUNT(*) AS complaint_count
            FROM customer_interactions
            WHERE interaction_type = 'Complaint'
            GROUP BY
                customer_id,
                DATE_FORMAT(interaction_date, '%Y-%m-01')
        """)

        complaint_rows = cursor.fetchall()

        complaint_map = {}

        for row in complaint_rows:

            complaint_map[
                (
                    row["customer_id"],
                    row["month"]
                )
            ] = row["complaint_count"]

        print(
            f"Complaint metric groups: "
            f"{len(complaint_map):,}"
        )

        # ====================================================
        # ENDING BALANCES
        # ====================================================

        print(
            "\nCalculating monthly ending balances..."
        )

        # We'll simplify: use a subquery to get the last transaction per customer per month
        cursor.execute("""
            SELECT
                t.customer_id,
                DATE_FORMAT(t.transaction_date, '%Y-%m-01') AS month,
                t.balance_after
            FROM transactions t
            INNER JOIN (
                SELECT
                    customer_id,
                    DATE_FORMAT(transaction_date, '%Y-%m-01') AS month,
                    MAX(transaction_date) AS max_date
                FROM transactions
                GROUP BY
                    customer_id,
                    DATE_FORMAT(transaction_date, '%Y-%m-01')
            ) latest
            ON t.customer_id = latest.customer_id
                AND DATE_FORMAT(t.transaction_date, '%Y-%m-01') = latest.month
                AND t.transaction_date = latest.max_date
        """)

        balance_rows = cursor.fetchall()

        balance_map = {}

        for row in balance_rows:

            balance_map[
                (
                    row["customer_id"],
                    row["month"]
                )
            ] = decimal(
                row["balance_after"]
            )

        print(
            f"Ending balance groups: "
            f"{len(balance_map):,}"
        )

        # ====================================================
        # BUILD METRICS
        # ====================================================

        print("\n")
        print("=" * 70)
        print("BUILDING MONTHLY CUSTOMER METRICS")
        print("=" * 70)

        metrics = []

        # Only create months where the customer has
        # actual banking activity.

        activity_keys = set()

        activity_keys.update(
            transaction_map.keys()
        )

        activity_keys.update(
            digital_map.keys()
        )

        activity_keys.update(
            atm_map.keys()
        )

        activity_keys.update(
            loan_map.keys()
        )

        activity_keys.update(
            fraud_map.keys()
        )

        activity_keys.update(
            complaint_map.keys()
        )

        print(
            f"\nUnique customer-month combinations: "
            f"{len(activity_keys):,}"
        )

        for index, key in enumerate(
            sorted(activity_keys),
            start=1
        ):

            customer_id, month = key

            txn = transaction_map.get(
                key
            )

            total_deposits = decimal(
                txn["total_deposits"]
            ) if txn else Decimal("0.00")

            total_withdrawals = decimal(
                txn["total_withdrawals"]
            ) if txn else Decimal("0.00")

            transaction_count = (
                txn["transaction_count"]
                if txn
                else 0
            )

            average_transaction = decimal(
                txn["average_transaction"]
            ) if txn else Decimal("0.00")

            largest_transaction = decimal(
                txn["largest_transaction"]
            ) if txn else Decimal("0.00")

            active_days = (
                txn["active_days"]
                if txn
                else 0
            )

            ending_balance = balance_map.get(
                key,
                Decimal("0.00")
            )

            digital_count = digital_map.get(
                key,
                0
            )

            atm_count = atm_map.get(
                key,
                0
            )

            loan_payment = loan_map.get(
                key,
                Decimal("0.00")
            )

            fraud_count = fraud_map.get(
                key,
                0
            )

            complaint_count = complaint_map.get(
                key,
                0
            )

            metrics.append(
                (
                    customer_id,
                    month,
                    ending_balance,
                    total_deposits,
                    total_withdrawals,
                    transaction_count,
                    digital_count,
                    atm_count,
                    loan_payment,
                    average_transaction,
                    largest_transaction,
                    fraud_count,
                    complaint_count,
                    active_days
                )
            )

            if index % 10000 == 0:

                print(
                    f"  Built {index:,} / "
                    f"{len(activity_keys):,}"
                )

        print(
            "\nMetric generation completed."
        )

        # ====================================================
        # INSERT
        # ====================================================

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO monthly_customer_metrics (
                customer_id,
                month,
                ending_balance,
                total_deposits,
                total_withdrawals,
                transaction_count,
                digital_transaction_count,
                atm_transaction_count,
                loan_payment_amount,
                average_transaction,
                largest_transaction,
                fraud_alert_count,
                customer_complaints,
                active_days
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE

                ending_balance =
                    VALUES(ending_balance),

                total_deposits =
                    VALUES(total_deposits),

                total_withdrawals =
                    VALUES(total_withdrawals),

                transaction_count =
                    VALUES(transaction_count),

                digital_transaction_count =
                    VALUES(digital_transaction_count),

                atm_transaction_count =
                    VALUES(atm_transaction_count),

                loan_payment_amount =
                    VALUES(loan_payment_amount),

                average_transaction =
                    VALUES(average_transaction),

                largest_transaction =
                    VALUES(largest_transaction),

                fraud_alert_count =
                    VALUES(fraud_alert_count),

                customer_complaints =
                    VALUES(customer_complaints),

                active_days =
                    VALUES(active_days)
        """

        batch_size = 1000

        for start in range(
            0,
            len(metrics),
            batch_size
        ):

            batch = metrics[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            completed = min(
                start + batch_size,
                len(metrics)
            )

            print(
                f"  {completed:,} / "
                f"{len(metrics):,} "
                f"({completed / len(metrics) * 100:6.2f}%)"
            )

        # ====================================================
        # VERIFICATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM monthly_customer_metrics
        """)

        count = cursor.fetchone()["count"]

        print(
            f"\nMonthly customer metric rows: "
            f"{count:,}"
        )

        cursor.execute("""
            SELECT
                customer_id,
                month,
                ending_balance,
                total_deposits,
                total_withdrawals,
                transaction_count,
                digital_transaction_count,
                atm_transaction_count,
                loan_payment_amount,
                average_transaction,
                largest_transaction,
                fraud_alert_count,
                customer_complaints,
                active_days
            FROM monthly_customer_metrics
            ORDER BY month DESC, customer_id
            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample metrics:\n")

        for row in rows:

            print(
                f"{row['customer_id']} | "
                f"{row['month']} | "
                f"Balance K{row['ending_balance']:,.2f} | "
                f"Deposits K{row['total_deposits']:,.2f} | "
                f"Withdrawals K{row['total_withdrawals']:,.2f} | "
                f"TXNs {row['transaction_count']} | "
                f"Digital {row['digital_transaction_count']} | "
                f"ATM {row['atm_transaction_count']} | "
                f"Loan K{row['loan_payment_amount']:,.2f} | "
                f"Fraud {row['fraud_alert_count']} | "
                f"Complaints {row['customer_complaints']}"
            )

        print(
            "\n✓ Monthly customer metrics "
            "successfully populated."
        )

    except Error as e:

        connection.rollback()

        print(
            f"\nMySQL Error: {e}"
        )

    finally:

        cursor.close()
        connection.close()

    print("\n")
    print("=" * 70)
    print(
        "KWACHA BANK CUSTOMER METRICS "
        "GENERATION FINISHED"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()