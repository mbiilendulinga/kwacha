import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta


# ============================================================
# KWACHA BANK
# SYNTHETIC CUSTOMER INTERACTION DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

TARGET_INTERACTIONS = 15000
RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)


# ============================================================
# INTERACTION TYPES
# ============================================================

INTERACTION_TYPES = [
    ("Enquiry", 15),
    ("Branch Visit", 14),
    ("Card Support", 9),
    ("Complaint", 8),
    ("Account Support", 8),
    ("Loan Enquiry", 7),
    ("Digital Banking Support", 6),
    ("Account Opening", 5),
    ("Loan Support", 5),
    ("Mobile Banking Support", 5),
    ("Transaction Dispute", 4),
    ("Internet Banking Support", 4),
    ("Fraud Report", 3),
    ("Address Update", 2),
    ("Account Closure", 2),
    ("KYC Update", 2),
    ("General Request", 1)
]


CHANNELS = [
    ("Branch", 30),
    ("Phone", 22),
    ("Mobile App", 12),
    ("Email", 10),
    ("WhatsApp", 8),
    ("Internet Banking", 8),
    ("ATM", 6),
    ("Social Media", 4)
]


CATEGORIES = [
    "Account",
    "Cards",
    "Loans",
    "Digital Banking",
    "Transactions",
    "Fraud",
    "KYC",
    "General"
]


STATUSES = [
    ("Resolved", 44),
    ("Closed", 28),
    ("In Progress", 10),
    ("Escalated", 8),
    ("Pending Customer", 5),
    ("Open", 5)
]


# ============================================================
# DATABASE
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
# WEIGHTED CHOICE
# ============================================================

def weighted_choice(options):

    values = [x[0] for x in options]
    weights = [x[1] for x in options]

    return random.choices(
        values,
        weights=weights,
        k=1
    )[0]


# ============================================================
# DESCRIPTION
# ============================================================

DESCRIPTIONS = {

    "Enquiry": [
        "Customer requested general banking information.",
        "Customer requested information about available banking services.",
        "Customer made an enquiry regarding account services.",
        "Customer requested information about banking charges."
    ],

    "Branch Visit": [
        "Customer visited branch for banking assistance.",
        "Customer visited branch for account-related services.",
        "Customer visited branch to speak with a banking officer."
    ],

    "Card Support": [
        "Customer requested assistance with bank card.",
        "Customer reported an issue with card usage.",
        "Customer requested card replacement.",
        "Customer reported a card transaction issue."
    ],

    "Complaint": [
        "Customer submitted a complaint regarding banking services.",
        "Customer complained about transaction processing time.",
        "Customer raised a service quality complaint.",
        "Customer complained about account-related charges."
    ],

    "Account Support": [
        "Customer requested assistance with account.",
        "Customer requested clarification regarding account activity.",
        "Customer required assistance with account services."
    ],

    "Loan Enquiry": [
        "Customer requested information about loan products.",
        "Customer enquired about loan eligibility.",
        "Customer requested information about loan repayment terms."
    ],

    "Digital Banking Support": [
        "Customer required assistance with digital banking.",
        "Customer reported an issue with internet banking.",
        "Customer requested assistance with online banking access."
    ],

    "Account Opening": [
        "Customer requested assistance opening an account.",
        "Customer initiated an account opening enquiry.",
        "Customer requested information about account opening requirements."
    ],

    "Loan Support": [
        "Customer requested assistance with existing loan.",
        "Customer requested clarification regarding loan repayment.",
        "Customer enquired about outstanding loan balance."
    ],

    "Mobile Banking Support": [
        "Customer reported an issue with mobile banking.",
        "Customer requested assistance with mobile banking.",
        "Customer required help accessing mobile banking."
    ],

    "Transaction Dispute": [
        "Customer disputed a transaction.",
        "Customer reported an incorrect transaction.",
        "Customer requested investigation of a transaction."
    ],

    "Internet Banking Support": [   # <-- added this key
        "Customer needed help with internet banking login.",
        "Customer reported an issue with online banking access.",
        "Customer requested assistance with internet banking features."
    ],

    "Fraud Report": [
        "Customer reported suspected fraudulent activity.",
        "Customer reported an unauthorised transaction.",
        "Customer reported suspicious account activity."
    ],

    "Address Update": [
        "Customer requested an address update.",
        "Customer requested customer information update."
    ],

    "Account Closure": [
        "Customer requested account closure.",
        "Customer enquired about account closure procedures."
    ],

    "KYC Update": [
        "Customer requested KYC information update.",
        "Customer submitted updated identification information."
    ],

    "General Request": [
        "Customer submitted a general service request.",
        "Customer requested assistance with banking services."
    ]
}


# ============================================================
# CATEGORY MAPPING
# ============================================================

CATEGORY_MAP = {

    "Enquiry": "General",
    "Branch Visit": "General",
    "Card Support": "Cards",
    "Complaint": "General",
    "Account Support": "Account",
    "Loan Enquiry": "Loans",
    "Digital Banking Support": "Digital Banking",
    "Account Opening": "Account",
    "Loan Support": "Loans",
    "Mobile Banking Support": "Digital Banking",
    "Transaction Dispute": "Transactions",
    "Internet Banking Support": "Digital Banking",
    "Fraud Report": "Fraud",
    "Address Update": "KYC",
    "Account Closure": "Account",
    "KYC Update": "KYC",
    "General Request": "General"
}


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC CUSTOMER INTERACTION DATA GENERATOR")
    print("=" * 70)

    print(f"\nTarget interactions: {TARGET_INTERACTIONS}")
    print(f"Random seed: {RANDOM_SEED}")

    print("\n")
    print("=" * 70)
    print("CONNECTING TO MYSQL")
    print("=" * 70)

    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor(dictionary=True)

    try:

        # --------------------------------------------------------
        # LOAD CUSTOMERS
        # --------------------------------------------------------

        print("\nLoading customers...")

        cursor.execute("""
            SELECT
                customer_id,
                customer_since,
                is_active
            FROM customers
        """)

        customers = cursor.fetchall()

        print(
            f"Loaded {len(customers):,} customers."
        )

        # --------------------------------------------------------
        # LOAD EMPLOYEES
        # --------------------------------------------------------

        print("\nLoading employees...")

        cursor.execute("""
            SELECT employee_id
            FROM employees
        """)

        employees = cursor.fetchall()

        print(
            f"Loaded {len(employees):,} employees."
        )

        # --------------------------------------------------------
        # LOAD BRANCHES (not used in insert, but kept for reference)
        # --------------------------------------------------------

        print("\nLoading branches...")

        cursor.execute("""
            SELECT branch_id
            FROM branches
        """)

        branches = cursor.fetchall()

        print(
            f"Loaded {len(branches):,} branches."
        )

        if not customers:
            print("\nNo customers found.")
            return

        # --------------------------------------------------------
        # GENERATE
        # --------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("GENERATING CUSTOMER INTERACTIONS")
        print("=" * 70)

        interactions = []

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2026, 8, 13)

        for i in range(1, TARGET_INTERACTIONS + 1):

            customer = random.choice(customers)

            interaction_type = weighted_choice(
                INTERACTION_TYPES
            )

            channel = weighted_choice(
                CHANNELS
            )

            category = CATEGORY_MAP[
                interaction_type
            ]

            # Make interaction date respect customer_since
            customer_since = customer["customer_since"]

            if customer_since:

                customer_start = datetime.combine(
                    customer_since,
                    datetime.min.time()
                )

                actual_start = max(
                    start_date,
                    customer_start
                )

            else:

                actual_start = start_date

            if actual_start > end_date:
                actual_start = end_date

            days_range = (
                end_date - actual_start
            ).days

            if days_range > 0:

                interaction_datetime = (
                    actual_start
                    + timedelta(
                        days=random.randint(
                            0,
                            days_range
                        ),
                        hours=random.randint(
                            7,
                            18
                        ),
                        minutes=random.randint(
                            0,
                            59
                        )
                    )
                )

            else:

                interaction_datetime = actual_start

            status = weighted_choice(
                STATUSES
            )

            description = random.choice(
                DESCRIPTIONS[
                    interaction_type
                ]
            )

            # Critical interactions are more likely to escalate
            if interaction_type == "Fraud Report":

                status = random.choices(
                    [
                        "Resolved",
                        "Closed",
                        "Escalated",
                        "In Progress"
                    ],
                    weights=[
                        25,
                        20,
                        40,
                        15
                    ],
                    k=1
                )[0]

            # Complaints tend to have higher resolution time
            if interaction_type == "Complaint":

                resolution_time = round(
                    random.uniform(2, 72),
                    2
                )

            else:

                resolution_time = round(
                    random.uniform(0.25, 36),
                    2
                )

            if status in [
                "Resolved",
                "Closed"
            ]:

                satisfaction_score = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[
                        3,
                        7,
                        20,
                        35,
                        35
                    ],
                    k=1
                )[0]

            elif status == "Escalated":

                satisfaction_score = random.choices(
                    [1, 2, 3, 4],
                    weights=[
                        25,
                        35,
                        30,
                        10
                    ],
                    k=1
                )[0]

            else:

                satisfaction_score = None

            employee_id = None

            if employees and random.random() < 0.75:

                employee_id = random.choice(
                    employees
                )["employee_id"]

            interactions.append(
                (
                    f"INT-{random.randint(10000000, 99999999)}-{i:05d}",
                    customer["customer_id"],
                    interaction_datetime,
                    interaction_type,
                    channel,
                    category,
                    description,
                    status,
                    resolution_time,
                    satisfaction_score,
                    employee_id
                )
            )

            if i % 1000 == 0:

                print(
                    f"  Generated {i:,} / "
                    f"{TARGET_INTERACTIONS:,}"
                )

        print("\nGeneration completed.")

        # --------------------------------------------------------
        # VALIDATION
        # --------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        print(
            f"\nInteractions generated: "
            f"{len(interactions):,}"
        )

        print("\nInteraction types:")

        counts = {}

        for row in interactions:

            key = row[3]

            counts[key] = counts.get(
                key,
                0
            ) + 1

        for key, value in sorted(
            counts.items(),
            key=lambda x: -x[1]
        ):

            print(
                f"  {key:<30} {value:,}"
            )

        # --------------------------------------------------------
        # INSERT
        # --------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO customer_interactions (
                interaction_id,
                customer_id,
                interaction_date,
                interaction_type,
                channel,
                category,
                description,
                resolution_status,
                resolution_time_hours,
                satisfaction_score,
                employee_id
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        batch_size = 1000

        for start in range(
            0,
            len(interactions),
            batch_size
        ):

            batch = interactions[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            completed = min(
                start + batch_size,
                len(interactions)
            )

            print(
                f"  {completed:,} / "
                f"{len(interactions):,} "
                f"({completed / len(interactions) * 100:6.2f}%)"
            )

        # --------------------------------------------------------
        # VERIFICATION
        # --------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM customer_interactions
        """)

        count = cursor.fetchone()["count"]

        print(
            f"\nCustomer interactions currently "
            f"in database: {count:,}"
        )

        cursor.execute("""
            SELECT
                interaction_id,
                customer_id,
                interaction_date,
                interaction_type,
                channel,
                category,
                resolution_status,
                satisfaction_score
            FROM customer_interactions
            ORDER BY interaction_date DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample interactions:\n")

        for row in rows:

            print(
                f"{row['interaction_id']} | "
                f"{row['customer_id']} | "
                f"{row['interaction_date']} | "
                f"{row['interaction_type']} | "
                f"{row['channel']} | "
                f"{row['category']} | "
                f"{row['resolution_status']} | "
                f"Score: {row['satisfaction_score']}"
            )

        print(
            "\n✓ Customer interaction table "
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
        "KWACHA BANK CUSTOMER INTERACTION "
        "GENERATION FINISHED"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()