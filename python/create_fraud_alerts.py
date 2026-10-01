import mysql.connector
from mysql.connector import Error
from decimal import Decimal
from datetime import datetime
import random
import string


# ============================================================
# KWACHA BANK
# SYNTHETIC FRAUD ALERT DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)


# ============================================================
# ID GENERATOR
# ============================================================

def generate_id(prefix, length=14):

    characters = string.ascii_uppercase + string.digits

    random_part = "".join(
        random.choices(
            characters,
            k=length
        )
    )

    return f"{prefix}-{random_part}"


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

        print(f"MySQL connection error: {e}")

        return None


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk_score(
    amount,
    transaction_type,
    channel,
    location,
    transaction_hour,
    international,
    failed_attempt,
    customer_average,
    digital_transaction
):

    score = 0

    # --------------------------------------------------------
    # Transaction amount
    # --------------------------------------------------------

    if amount >= 100000:
        score += 25

    elif amount >= 50000:
        score += 18

    elif amount >= 25000:
        score += 10

    elif amount >= 10000:
        score += 5

    # --------------------------------------------------------
    # Transaction compared with customer's normal behavior
    # --------------------------------------------------------

    if customer_average and customer_average > 0:

        ratio = amount / customer_average

        if ratio >= 10:
            score += 25

        elif ratio >= 5:
            score += 18

        elif ratio >= 3:
            score += 10

    # --------------------------------------------------------
    # International activity
    # --------------------------------------------------------

    if international:
        score += 20

    # --------------------------------------------------------
    # Night activity
    # --------------------------------------------------------

    if transaction_hour >= 0 and transaction_hour < 5:
        score += 15

    elif transaction_hour >= 22:
        score += 10

    # --------------------------------------------------------
    # Digital transactions
    # --------------------------------------------------------

    if digital_transaction:
        score += 5

    # --------------------------------------------------------
    # Failed attempt
    # --------------------------------------------------------

    if failed_attempt:
        score += 15

    # --------------------------------------------------------
    # Transaction type
    # --------------------------------------------------------

    if transaction_type in [
        "Transfer",
        "International Transfer",
        "Cash Withdrawal",
        "Card Payment"
    ]:

        score += 5

    # --------------------------------------------------------
    # Channel
    # --------------------------------------------------------

    if channel in [
        "Internet Banking",
        "Mobile Banking",
        "Banking App",
        "USSD"
    ]:

        score += 3

    # Add natural variation

    score += random.randint(
        -5,
        5
    )

    score = max(
        1,
        min(
            100,
            score
        )
    )

    return score


# ============================================================
# ALERT TYPE
# ============================================================

def determine_alert_type(
    amount,
    international,
    transaction_hour,
    failed_attempt,
    unusual_amount,
    digital_transaction
):

    possibilities = []

    if unusual_amount:

        possibilities.append(
            "Unusually Large Transaction"
        )

    if international:

        possibilities.append(
            "International Activity"
        )

    if transaction_hour >= 22 or transaction_hour < 5:

        possibilities.append(
            "Unusual Transaction Time"
        )

    if failed_attempt:

        possibilities.append(
            "Multiple Failed Attempts"
        )

    if digital_transaction:

        possibilities.append(
            "Suspicious Digital Activity"
        )

    possibilities.extend([
        "Unusual Transaction Pattern",
        "Potential Account Takeover",
        "Velocity Anomaly",
        "Transaction Behaviour Anomaly"
    ])

    return random.choice(
        possibilities
    )


# ============================================================
# SEVERITY
# ============================================================

def determine_severity(risk_score):

    if risk_score >= 80:

        return "Critical"

    elif risk_score >= 60:

        return "High"

    elif risk_score >= 40:

        return "Medium"

    return "Low"


# ============================================================
# DETECTION METHOD
# ============================================================

def determine_detection_method():

    return random.choices(

        [
            "Rule Engine",
            "Machine Learning",
            "Behavioural Analytics",
            "Velocity Monitoring",
            "Manual Review",
            "Transaction Monitoring"
        ],

        weights=[
            25,
            25,
            20,
            12,
            5,
            13
        ],

        k=1

    )[0]


# ============================================================
# INVESTIGATION STATUS
# ============================================================

def determine_investigation_status(
    risk_score,
    confirmed_fraud
):

    if confirmed_fraud:

        return random.choice([
            "Confirmed Fraud",
            "Account Restricted",
            "Under Investigation",
            "Resolved"
        ])

    if risk_score >= 70:

        return random.choice([
            "Under Investigation",
            "False Positive",
            "Customer Contacted"
        ])

    if risk_score >= 40:

        return random.choice([
            "Under Review",
            "False Positive",
            "Closed"
        ])

    return random.choice([
        "Closed",
        "False Positive",
        "Monitoring"
    ])


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC FRAUD ALERT DATA GENERATOR")
    print("=" * 70)

    print(
        f"\nRandom seed: {RANDOM_SEED}"
    )

    print("\n")
    print("=" * 70)
    print("CONNECTING TO MYSQL")
    print("=" * 70)

    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # ====================================================
        # LOAD TRANSACTIONS
        # ====================================================

        print("\nLoading transactions...")

        cursor.execute("""
            SELECT
                transaction_id,
                account_id,
                customer_id,
                transaction_date,
                transaction_type,
                amount,
                channel,
                transaction_status,
                location
            FROM transactions
        """)

        transactions = cursor.fetchall()

        print(
            f"Loaded {len(transactions):,} transactions."
        )

        if not transactions:

            print(
                "\nNo transactions found."
            )

            return

        # ====================================================
        # CUSTOMER AVERAGES
        # ====================================================

        print(
            "\nCalculating customer transaction behaviour..."
        )

        cursor.execute("""
            SELECT
                customer_id,
                AVG(amount) AS average_transaction
            FROM transactions
            WHERE transaction_status = 'Successful'
            GROUP BY customer_id
        """)

        customer_averages = {}

        for row in cursor.fetchall():

            customer_averages[
                row["customer_id"]
            ] = float(
                row["average_transaction"]
            )

        print(
            f"Calculated behaviour for "
            f"{len(customer_averages):,} customers."
        )

        # ====================================================
        # LOAD DIGITAL TRANSACTIONS
        # ====================================================

        print(
            "\nLoading digital transaction references..."
        )

        cursor.execute("""
            SELECT transaction_id
            FROM digital_transactions
        """)

        digital_transaction_ids = {
            row["transaction_id"]
            for row in cursor.fetchall()
        }

        print(
            f"Digital transaction references: "
            f"{len(digital_transaction_ids):,}"
        )

        # ====================================================
        # GENERATE ALERTS
        # ====================================================

        print("\n")
        print("=" * 70)
        print("GENERATING FRAUD ALERTS")
        print("=" * 70)

        generated = []

        alert_type_counts = {}
        severity_counts = {}
        method_counts = {}
        fraud_count = 0

        # We don't alert on every transaction.
        # Roughly 2.5% of transactions become alerts.

        alert_rate = 0.025

        for index, transaction in enumerate(
            transactions,
            start=1
        ):

            amount = float(
                transaction["amount"]
            )

            customer_id = (
                transaction["customer_id"]
            )

            customer_average = (
                customer_averages.get(
                    customer_id,
                    0
                )
            )

            transaction_datetime = (
                transaction["transaction_date"]
            )

            transaction_hour = (
                transaction_datetime.hour
            )

            international = (
                transaction["location"] is not None
                and transaction["location"] not in [
                    "Lusaka",
                    "Kitwe",
                    "Ndola",
                    "Livingstone",
                    "Kabwe",
                    "Chipata",
                    "Chingola",
                    "Mufulira",
                    "Solwezi",
                    "Mazabuka",
                    "Kasama",
                    "Mongu",
                    "Mansa",
                    "Luanshya",
                    "Choma",
                    "Petauke",
                    "Kapiri Mposhi",
                    "Mkushi",
                    "Mpika",
                    "Kafue"
                ]
            )

            failed_attempt = (
                transaction["transaction_status"]
                in [
                    "Failed",
                    "Declined"
                ]
            )

            unusual_amount = False

            if customer_average > 0:

                if amount >= customer_average * 3:

                    unusual_amount = True

            digital_transaction = (
                transaction["transaction_id"]
                in digital_transaction_ids
            )

            # ------------------------------------------------
            # Calculate probability of alert
            # ------------------------------------------------

            probability = alert_rate

            if unusual_amount:
                probability += 0.025

            if international:
                probability += 0.015

            if transaction_hour >= 22:
                probability += 0.01

            if transaction_hour < 5:
                probability += 0.015

            if failed_attempt:
                probability += 0.01

            if amount >= 100000:
                probability += 0.015

            # ------------------------------------------------
            # Decide whether alert is generated
            # ------------------------------------------------

            if random.random() > probability:

                continue

            # ------------------------------------------------
            # Risk score
            # ------------------------------------------------

            risk_score = calculate_risk_score(

                amount,

                transaction[
                    "transaction_type"
                ],

                transaction[
                    "channel"
                ],

                transaction[
                    "location"
                ],

                transaction_hour,

                international,

                failed_attempt,

                customer_average,

                digital_transaction
            )

            severity = determine_severity(
                risk_score
            )

            # ------------------------------------------------
            # Confirmed fraud
            # ------------------------------------------------

            # Most alerts are NOT confirmed fraud.

            fraud_probability = 0.02

            if risk_score >= 80:

                fraud_probability = 0.18

            elif risk_score >= 60:

                fraud_probability = 0.08

            elif risk_score >= 40:

                fraud_probability = 0.035

            confirmed_fraud = (
                random.random()
                < fraud_probability
            )

            if confirmed_fraud:

                fraud_count += 1

            # ------------------------------------------------
            # Alert information
            # ------------------------------------------------

            alert_type = determine_alert_type(

                amount,

                international,

                transaction_hour,

                failed_attempt,

                unusual_amount,

                digital_transaction
            )

            detection_method = (
                determine_detection_method()
            )

            investigation_status = (
                determine_investigation_status(
                    risk_score,
                    confirmed_fraud
                )
            )

            # ------------------------------------------------
            # Resolution date
            # ------------------------------------------------

            resolution_date = None

            if investigation_status in [
                "Confirmed Fraud",
                "False Positive",
                "Closed",
                "Resolved"
            ]:

                resolution_date = (
                    transaction_datetime
                )

                # Add investigation time

                from datetime import timedelta

                resolution_date += timedelta(
                    hours=random.randint(
                        2,
                        240
                    )
                )

            # ------------------------------------------------
            # Build row
            # ------------------------------------------------

            row = (

                generate_id(
                    "ALT",
                    14
                ),

                transaction[
                    "transaction_id"
                ],

                customer_id,

                transaction_datetime,

                alert_type,

                Decimal(
                    str(
                        round(
                            risk_score,
                            2
                        )
                    )
                ),

                severity,

                detection_method,

                investigation_status,

                confirmed_fraud,

                resolution_date
            )

            generated.append(
                row
            )

            alert_type_counts[
                alert_type
            ] = (
                alert_type_counts.get(
                    alert_type,
                    0
                ) + 1
            )

            severity_counts[
                severity
            ] = (
                severity_counts.get(
                    severity,
                    0
                ) + 1
            )

            method_counts[
                detection_method
            ] = (
                method_counts.get(
                    detection_method,
                    0
                ) + 1
            )

            if index % 100000 == 0:

                print(
                    f"  Processed "
                    f"{index:,} transactions..."
                )

        print(
            "\nGeneration completed."
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        print(
            f"\nTransactions analysed: "
            f"{len(transactions):,}"
        )

        print(
            f"Fraud alerts generated: "
            f"{len(generated):,}"
        )

        print(
            f"Confirmed fraud cases: "
            f"{fraud_count:,}"
        )

        if generated:

            print(
                f"Alert rate: "
                f"{len(generated) / len(transactions) * 100:.2f}%"
            )

        print("\nSeverity:")

        for severity, count in sorted(
            severity_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            print(
                f"  {severity:<12}"
                f"{count:>7,}"
            )

        print("\nAlert types:")

        for alert_type, count in sorted(
            alert_type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            print(
                f"  {alert_type:<35}"
                f"{count:>7,}"
            )

        print("\nDetection methods:")

        for method, count in sorted(
            method_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            print(
                f"  {method:<25}"
                f"{count:>7,}"
            )

        # ====================================================
        # INSERT
        # ====================================================

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """

            INSERT INTO fraud_alerts (

                alert_id,
                transaction_id,
                customer_id,
                alert_datetime,
                alert_type,
                risk_score,
                severity,
                detection_method,
                investigation_status,
                confirmed_fraud,
                resolution_date

            )

            VALUES (

                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s

            )

        """

        batch_size = 1000

        for start in range(
            0,
            len(generated),
            batch_size
        ):

            batch = generated[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            inserted = min(
                start + batch_size,
                len(generated)
            )

            print(
                f"  {inserted:,} / "
                f"{len(generated):,}"
                f" ({inserted / len(generated) * 100:6.2f}%)"
            )

        # ====================================================
        # DATABASE VERIFICATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*)
            FROM fraud_alerts
        """)

        count = cursor.fetchone()["COUNT(*)"]

        print(
            f"\nFraud alerts currently "
            f"in database: {count:,}"
        )

        cursor.execute("""
            SELECT
                f.alert_id,
                f.transaction_id,
                f.customer_id,
                CONCAT(
                    c.first_name,
                    ' ',
                    c.last_name
                ) AS customer_name,
                f.alert_type,
                f.risk_score,
                f.severity,
                f.detection_method,
                f.investigation_status,
                f.confirmed_fraud
            FROM fraud_alerts f

            JOIN customers c
                ON f.customer_id = c.customer_id

            ORDER BY RAND()

            LIMIT 10
        """)

        samples = cursor.fetchall()

        print("\nSample fraud alerts:\n")

        for row in samples:

            print(
                f"{row['alert_id']} | "
                f"{row['customer_name']} | "
                f"{row['alert_type']} | "
                f"Risk: {row['risk_score']} | "
                f"{row['severity']} | "
                f"{row['detection_method']} | "
                f"{row['investigation_status']} | "
                f"Fraud: "
                f"{'YES' if row['confirmed_fraud'] else 'NO'}"
            )

        print(
            "\n✓ Fraud alert table "
            "successfully populated."
        )

    except Error as e:

        connection.rollback()

        print(
            f"\nMySQL Error: {e}"
        )

    except Exception as e:

        connection.rollback()

        print(
            f"\nUnexpected Error: {e}"
        )

    finally:

        cursor.close()
        connection.close()

    print("\n")
    print("=" * 70)
    print(
        "KWACHA BANK FRAUD ALERT "
        "GENERATION FINISHED"
    )
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()