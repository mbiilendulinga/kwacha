import mysql.connector
from mysql.connector import Error

from datetime import datetime, date, timedelta
from decimal import Decimal
import random
import string


# ============================================================
# KWACHA BANK
# SYNTHETIC TRANSACTION DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)

# ------------------------------------------------------------
# DATASET SIZE
# ------------------------------------------------------------

TARGET_TRANSACTIONS = 1_000_000

# Historical period
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 8, 13)


# ============================================================
# GENERAL HELPERS
# ============================================================

def random_transaction_id(existing_ids):

    """
    Creates IDs such as:

        TXN7F3A91K204
        TXN2M8Q51Z773

    rather than sequential IDs.
    """

    characters = (
        string.ascii_uppercase
        +
        string.digits
    )

    while True:

        suffix = "".join(
            random.choices(
                characters,
                k=10
            )
        )

        transaction_id = (
            "TXN" + suffix
        )

        if transaction_id not in existing_ids:

            existing_ids.add(
                transaction_id
            )

            return transaction_id


def random_reference_number():

    characters = (
        string.ascii_uppercase
        +
        string.digits
    )

    return (
        "REF"
        +
        "".join(
            random.choices(
                characters,
                k=12
            )
        )
    )


def random_date(start_date, end_date):

    days = (
        end_date - start_date
    ).days

    return (
        start_date
        +
        timedelta(
            days=random.randint(
                0,
                days
            )
        )
    )


def random_datetime_for_date(transaction_date):

    hour = random.choices(
        range(24),
        weights=[
            1, 1, 1, 1, 1, 2,
            3, 5, 7, 8, 8, 8,
            8, 8, 9, 9, 10, 9,
            8, 7, 6, 4, 3, 2
        ],
        k=1
    )[0]

    minute = random.randint(
        0,
        59
    )

    second = random.randint(
        0,
        59
    )

    return datetime(
        transaction_date.year,
        transaction_date.month,
        transaction_date.day,
        hour,
        minute,
        second
    )


# ============================================================
# TRANSACTION TYPES
# ============================================================

DEPOSIT_TYPES = [
    "Cash Deposit",
    "Salary Credit",
    "Bank Transfer In",
    "Mobile Money Deposit",
    "Interest Credit"
]

WITHDRAWAL_TYPES = [
    "Cash Withdrawal",
    "ATM Withdrawal",
    "Bank Transfer Out",
    "Mobile Money Transfer",
    "Bill Payment",
    "POS Purchase",
    "Online Purchase",
    "Bank Charge"
]


# ============================================================
# AMOUNT GENERATION
# ============================================================

def generate_amount(
    customer,
    transaction_type
):

    income = customer["monthly_income"]

    if income is None:
        income = Decimal("5000")

    income = float(income)

    # --------------------------------------------------------
    # Salary
    # --------------------------------------------------------

    if transaction_type == "Salary Credit":

        amount = random.gauss(
            income,
            income * 0.04
        )

        return round(
            max(
                1000,
                amount
            ),
            2
        )

    # --------------------------------------------------------
    # Bank charges
    # --------------------------------------------------------

    if transaction_type == "Bank Charge":

        return round(
            random.uniform(
                5,
                150
            ),
            2
        )

    # --------------------------------------------------------
    # ATM withdrawals
    # --------------------------------------------------------

    if transaction_type == "ATM Withdrawal":

        return round(
            random.choice([
                100,
                200,
                300,
                500,
                800,
                1000,
                1500,
                2000,
                2500,
                3000,
                4000,
                5000
            ]),
            2
        )

    # --------------------------------------------------------
    # POS
    # --------------------------------------------------------

    if transaction_type == "POS Purchase":

        return round(
            max(
                10,
                random.lognormvariate(
                    5.2,
                    0.75
                )
            ),
            2
        )

    # --------------------------------------------------------
    # Online purchase
    # --------------------------------------------------------

    if transaction_type == "Online Purchase":

        return round(
            max(
                20,
                random.lognormvariate(
                    5.5,
                    0.9
                )
            ),
            2
        )

    # --------------------------------------------------------
    # Deposits
    # --------------------------------------------------------

    if transaction_type in [
        "Cash Deposit",
        "Bank Transfer In",
        "Mobile Money Deposit"
    ]:

        amount = random.lognormvariate(
            7.5,
            1.0
        )

        # Income influence
        amount *= random.uniform(
            0.5,
            1.5
        )

        return round(
            max(
                50,
                amount
            ),
            2
        )

    # --------------------------------------------------------
    # Transfers
    # --------------------------------------------------------

    if transaction_type in [
        "Bank Transfer Out",
        "Mobile Money Transfer"
    ]:

        amount = random.lognormvariate(
            7.0,
            0.9
        )

        return round(
            max(
                20,
                amount
            ),
            2
        )

    # --------------------------------------------------------
    # Bill payments
    # --------------------------------------------------------

    if transaction_type == "Bill Payment":

        return round(
            random.uniform(
                50,
                5000
            ),
            2
        )

    # --------------------------------------------------------
    # Interest
    # --------------------------------------------------------

    if transaction_type == "Interest Credit":

        return round(
            random.uniform(
                20,
                1500
            ),
            2
        )

    return round(
        random.uniform(
            50,
            5000
        ),
        2
    )


# ============================================================
# CUSTOMER ACTIVITY
# ============================================================

def customer_activity_weight(customer):

    """
    Makes transaction frequency depend on
    customer characteristics.
    """

    weight = 1.0

    segment = customer["customer_segment"]

    employment = customer["employment_status"]

    # --------------------------------------------------------
    # Segment
    # --------------------------------------------------------

    if segment == "Affluent":
        weight *= 3.5

    elif segment == "Mass Affluent":
        weight *= 2.5

    elif segment == "Business":
        weight *= 3.0

    elif segment == "Mass Market":
        weight *= 1.5

    elif segment == "Entry Level":
        weight *= 1.0

    elif segment == "Youth":
        weight *= 0.8

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    if employment == "Employed":
        weight *= 1.3

    elif employment == "Self-employed":
        weight *= 1.5

    elif employment == "Student":
        weight *= 0.7

    elif employment == "Unemployed":
        weight *= 0.5

    elif employment == "Retired":
        weight *= 0.6

    return weight


# ============================================================
# TRANSACTION TYPE
# ============================================================

def choose_transaction_type(
    customer,
    transaction_date
):

    employment = customer[
        "employment_status"
    ]

    segment = customer[
        "customer_segment"
    ]

    day = transaction_date.day

    # --------------------------------------------------------
    # Salary customers around month end
    # --------------------------------------------------------

    if employment == "Employed":

        if day >= 24 or day <= 3:

            if random.random() < 0.28:

                return "Salary Credit"

    # --------------------------------------------------------
    # Business customers
    # --------------------------------------------------------

    if segment == "Business":

        choices = [
            "Cash Deposit",
            "Bank Transfer In",
            "Bank Transfer Out",
            "POS Purchase",
            "Bill Payment",
            "Mobile Money Transfer",
            "Bank Charge"
        ]

        weights = [
            20,
            20,
            18,
            15,
            10,
            12,
            5
        ]

        return random.choices(
            choices,
            weights=weights,
            k=1
        )[0]

    # --------------------------------------------------------
    # General customers
    # --------------------------------------------------------

    choices = [
        "Cash Deposit",
        "Cash Withdrawal",
        "ATM Withdrawal",
        "Bank Transfer In",
        "Bank Transfer Out",
        "Mobile Money Transfer",
        "Bill Payment",
        "POS Purchase",
        "Online Purchase",
        "Bank Charge"
    ]

    weights = [
        8,
        7,
        12,
        8,
        8,
        8,
        10,
        25,
        10,
        4
    ]

    return random.choices(
        choices,
        weights=weights,
        k=1
    )[0]


# ============================================================
# CHANNEL
# ============================================================

def determine_channel(
    transaction_type
):

    if transaction_type == "ATM Withdrawal":

        return "ATM"

    if transaction_type == "POS Purchase":

        return "POS"

    if transaction_type == "Online Purchase":

        return "Internet Banking"

    if transaction_type in [
        "Mobile Money Transfer",
        "Mobile Money Deposit"
    ]:

        return "Mobile Banking"

    if transaction_type in [
        "Cash Deposit",
        "Cash Withdrawal"
    ]:

        return random.choices(
            [
                "Branch",
                "ATM"
            ],
            weights=[
                65,
                35
            ],
            k=1
        )[0]

    if transaction_type in [
        "Bank Transfer In",
        "Bank Transfer Out"
    ]:

        return random.choice([
            "Mobile Banking",
            "Internet Banking",
            "Branch"
        ])

    if transaction_type == "Bill Payment":

        return random.choice([
            "Mobile Banking",
            "Internet Banking",
            "Branch"
        ])

    return "System"


# ============================================================
# LOCATION
# ============================================================

def generate_location(branch):

    return (
        f"{branch['city']}, "
        f"{branch['province']}"
    )


# ============================================================
# TRANSACTION STATUS
# ============================================================

def determine_status():

    return random.choices(
        [
            "Successful",
            "Failed",
            "Pending",
            "Reversed"
        ],
        weights=[
            96,
            2,
            1,
            1
        ],
        k=1
    )[0]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC TRANSACTION DATA GENERATOR")
    print("=" * 70)

    print(
        f"\nTarget transactions: "
        f"{TARGET_TRANSACTIONS:,}"
    )

    print(
        f"Random seed: "
        f"{RANDOM_SEED}"
    )

    connection = None
    cursor = None

    try:

        # ====================================================
        # CONNECTION
        # ====================================================

        print("\nConnecting to MySQL...")

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor(
            dictionary=True
        )

        # ====================================================
        # LOAD CUSTOMERS
        # ====================================================

        print("Loading customers...")

        cursor.execute("""
            SELECT
                customer_id,
                first_name,
                last_name,
                employment_status,
                monthly_income,
                customer_segment
            FROM customers
        """)

        customers = cursor.fetchall()

        customer_lookup = {
            c["customer_id"]: c
            for c in customers
        }

        print(
            f"Loaded {len(customers):,} customers."
        )

        # ====================================================
        # LOAD ACCOUNTS
        # ====================================================

        print("Loading accounts...")

        cursor.execute("""
            SELECT
                account_id,
                customer_id,
                account_type_id,
                branch_id,
                account_number,
                open_date,
                current_balance,
                available_balance,
                status
            FROM accounts
            WHERE status != 'Closed'
        """)

        accounts = cursor.fetchall()

        print(
            f"Loaded {len(accounts):,} active/usable accounts."
        )

        # ====================================================
        # LOAD BRANCHES
        # ====================================================

        print("Loading branches...")

        cursor.execute("""
            SELECT
                branch_id,
                branch_name,
                province,
                district,
                city
            FROM branches
        """)

        branches = cursor.fetchall()

        branch_lookup = {
            b["branch_id"]: b
            for b in branches
        }

        print(
            f"Loaded {len(branches):,} branches."
        )

        # ====================================================
        # PREPARE ACCOUNT WEIGHTS
        # ====================================================

        weighted_accounts = []

        for account in accounts:

            customer = customer_lookup.get(
                account["customer_id"]
            )

            if customer is None:
                continue

            weight = customer_activity_weight(
                customer
            )

            weighted_accounts.append(
                (
                    account,
                    weight
                )
            )

        account_objects = [
            item[0]
            for item in weighted_accounts
        ]

        account_weights = [
            item[1]
            for item in weighted_accounts
        ]

        # ====================================================
        # GENERATE
        # ====================================================

        print("\n")
        print("=" * 70)
        print("GENERATING TRANSACTIONS")
        print("=" * 70)

        generated = []

        existing_ids = set()

        # Keep track of balances while generating
        balances = {}

        for account in account_objects:

            starting_balance = account[
                "current_balance"
            ]

            if starting_balance is None:
                starting_balance = Decimal("0")

            balances[
                account["account_id"]
            ] = Decimal(
                starting_balance
            )

        type_counts = {}
        channel_counts = {}
        status_counts = {}

        # ====================================================
        # GENERATION LOOP
        # ====================================================

        for i in range(
            TARGET_TRANSACTIONS
        ):

            account = random.choices(
                account_objects,
                weights=account_weights,
                k=1
            )[0]

            customer = customer_lookup[
                account["customer_id"]
            ]

            branch = branch_lookup.get(
                account["branch_id"]
            )

            # ------------------------------------------------
            # Date
            # ------------------------------------------------

            transaction_date = random_date(
                max(
                    START_DATE,
                    account["open_date"]
                ),
                END_DATE
            )

            transaction_datetime = (
                random_datetime_for_date(
                    transaction_date
                )
            )

            # ------------------------------------------------
            # Type
            # ------------------------------------------------

            transaction_type = (
                choose_transaction_type(
                    customer,
                    transaction_date
                )
            )

            amount = generate_amount(
                customer,
                transaction_type
            )

            amount = Decimal(
                str(amount)
            )

            # ------------------------------------------------
            # Direction
            # ------------------------------------------------

            credit_types = [
                "Cash Deposit",
                "Salary Credit",
                "Bank Transfer In",
                "Mobile Money Deposit",
                "Interest Credit"
            ]

            is_credit = (
                transaction_type
                in credit_types
            )

            # ------------------------------------------------
            # Balance
            # ------------------------------------------------

            balance_before = balances[
                account["account_id"]
            ]

            # Avoid ridiculous negative balances.
            #
            # If withdrawal exceeds available funds,
            # occasionally allow overdraft for eligible
            # accounts, otherwise turn it into a failed
            # transaction.
            # ------------------------------------------------

            if not is_credit:

                overdraft_limit = Decimal(
                    str(
                        account.get(
                            "overdraft_limit",
                            0
                        ) or 0
                    )
                )

                if (
                    balance_before
                    -
                    amount
                    <
                    -overdraft_limit
                ):

                    transaction_status = (
                        "Failed"
                    )

                    balance_after = (
                        balance_before
                    )

                else:

                    transaction_status = (
                        determine_status()
                    )

                    if transaction_status in [
                        "Failed",
                        "Pending"
                    ]:

                        balance_after = (
                            balance_before
                        )

                    else:

                        balance_after = (
                            balance_before
                            -
                            amount
                        )

            else:

                transaction_status = (
                    determine_status()
                )

                if transaction_status in [
                    "Failed",
                    "Pending"
                ]:

                    balance_after = (
                        balance_before
                    )

                else:

                    balance_after = (
                        balance_before
                        +
                        amount
                    )

            # ------------------------------------------------
            # Channel
            # ------------------------------------------------

            channel = determine_channel(
                transaction_type
            )

            # ------------------------------------------------
            # Branch
            # ------------------------------------------------

            branch_id = (
                account["branch_id"]
            )

            # ------------------------------------------------
            # Location
            # ------------------------------------------------

            if branch:

                location = generate_location(
                    branch
                )

            else:

                location = None

            # ------------------------------------------------
            # Merchant
            # ------------------------------------------------

            merchant_id = None

            if transaction_type in [
                "POS Purchase",
                "Online Purchase"
            ]:

                # Merchant IDs will correspond to
                # merchants generated later.
                merchant_id = (
                    "MER"
                    +
                    str(
                        random.randint(
                            1,
                            5000
                        )
                    ).zfill(6)
                )

            # ------------------------------------------------
            # Reference
            # ------------------------------------------------

            reference_number = (
                random_reference_number()
            )

            # ------------------------------------------------
            # Reversal
            # ------------------------------------------------

            is_reversal = (
                transaction_status
                == "Reversed"
            )

            # ------------------------------------------------
            # ID
            # ------------------------------------------------

            transaction_id = (
                random_transaction_id(
                    existing_ids
                )
            )

            # ------------------------------------------------
            # Update balance
            # ------------------------------------------------

            balances[
                account["account_id"]
            ] = balance_after

            # ------------------------------------------------
            # Store
            # ------------------------------------------------

            generated.append(
                (
                    transaction_id,
                    account["account_id"],
                    customer["customer_id"],
                    transaction_datetime,
                    transaction_type,
                    amount,
                    "ZMW",
                    channel,
                    branch_id,
                    merchant_id,
                    reference_number,
                    balance_before,
                    balance_after,
                    transaction_status,
                    location,
                    is_reversal
                )
            )

            # ------------------------------------------------
            # Statistics
            # ------------------------------------------------

            type_counts[
                transaction_type
            ] = (
                type_counts.get(
                    transaction_type,
                    0
                ) + 1
            )

            channel_counts[
                channel
            ] = (
                channel_counts.get(
                    channel,
                    0
                ) + 1
            )

            status_counts[
                transaction_status
            ] = (
                status_counts.get(
                    transaction_status,
                    0
                ) + 1
            )

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if (
                (i + 1) % 50_000
                == 0
            ):

                percentage = (
                    (i + 1)
                    /
                    TARGET_TRANSACTIONS
                ) * 100

                print(
                    f"  {i + 1:,} / "
                    f"{TARGET_TRANSACTIONS:,} "
                    f"({percentage:6.2f}%)"
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
            f"\nTransactions generated: "
            f"{len(generated):,}"
        )

        print("\nTransaction types:")

        for transaction_type, count in sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            percentage = (
                count
                /
                len(generated)
            ) * 100

            print(
                f"  {transaction_type:<25}"
                f"{count:>10,} "
                f"({percentage:5.2f}%)"
            )

        print("\nChannels:")

        for channel, count in sorted(
            channel_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            print(
                f"  {channel:<25}"
                f"{count:>10,}"
            )

        print("\nStatuses:")

        for status, count in sorted(
            status_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            print(
                f"  {status:<25}"
                f"{count:>10,}"
            )

        # ====================================================
        # INSERT
        # ====================================================

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        cursor.close()

        cursor = connection.cursor()

        insert_sql = """
            INSERT INTO transactions (
                transaction_id,
                account_id,
                customer_id,
                transaction_date,
                transaction_type,
                amount,
                currency,
                channel,
                branch_id,
                merchant_id,
                reference_number,
                balance_before,
                balance_after,
                transaction_status,
                location,
                is_reversal
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        batch_size = 5000

        total = len(
            generated
        )

        for start in range(
            0,
            total,
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

            end = min(
                start + batch_size,
                total
            )

            percentage = (
                end / total
            ) * 100

            if (
                end % 50_000 == 0
                or end == total
            ):

                print(
                    f"  {end:,} / "
                    f"{total:,} "
                    f"({percentage:6.2f}%)"
                )

        # ====================================================
        # UPDATE ACCOUNT BALANCES
        # ====================================================

        print(
            "\nUpdating account balances..."
        )

        update_sql = """
            UPDATE accounts
            SET
                current_balance = %s,
                available_balance = %s
            WHERE account_id = %s
        """

        balance_updates = []

        for account_id, balance in balances.items():

            # Available balance cannot be negative
            # unless the account has an overdraft facility.

            available = max(
                Decimal("0"),
                balance
            )

            balance_updates.append(
                (
                    balance,
                    available,
                    account_id
                )
            )

        for start in range(
            0,
            len(balance_updates),
            batch_size
        ):

            batch = balance_updates[
                start:start + batch_size
            ]

            cursor.executemany(
                update_sql,
                batch
            )

            connection.commit()

        # ====================================================
        # VERIFICATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions
        """)

        transaction_count = (
            cursor.fetchone()[0]
        )

        print(
            f"\nTransactions currently "
            f"in database: "
            f"{transaction_count:,}"
        )

        cursor.execute("""
            SELECT
                AVG(amount),
                MAX(amount),
                MIN(amount)
            FROM transactions
        """)

        stats = cursor.fetchone()

        print(
            f"Average transaction: "
            f"K{float(stats[0]):,.2f}"
        )

        print(
            f"Largest transaction: "
            f"K{float(stats[1]):,.2f}"
        )

        print(
            f"Smallest transaction: "
            f"K{float(stats[2]):,.2f}"
        )

        # ====================================================
        # SAMPLE
        # ====================================================

        cursor.execute("""
            SELECT
                t.transaction_id,
                c.first_name,
                c.last_name,
                t.transaction_date,
                t.transaction_type,
                t.amount,
                t.channel,
                t.transaction_status,
                t.balance_before,
                t.balance_after
            FROM transactions t

            JOIN customers c
                ON t.customer_id =
                   c.customer_id

            ORDER BY RAND()

            LIMIT 10
        """)

        samples = cursor.fetchall()

        print("\nSample transactions:\n")

        for row in samples:

            print(
                f"{row[0]} | "
                f"{row[1]} {row[2]} | "
                f"{row[3]} | "
                f"{row[4]} | "
                f"K{float(row[5]):,.2f} | "
                f"{row[6]} | "
                f"{row[7]} | "
                f"K{float(row[8]):,.2f} -> "
                f"K{float(row[9]):,.2f}"
            )

        print(
            "\n✓ Transaction table successfully populated."
        )

    except Error as e:

        if connection:
            connection.rollback()

        print(
            f"\nMySQL Error: {e}"
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            f"\nUnexpected Error: {e}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    print("\n")
    print("=" * 70)
    print(
        "KWACHA BANK TRANSACTION "
        "GENERATION FINISHED"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()