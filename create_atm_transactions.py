import mysql.connector
from mysql.connector import Error
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from collections import Counter, defaultdict

# ============================================================
# KWACHA BANK
# SYNTHETIC ATM TRANSACTION DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

# Approximately 400,000 ATM records
TARGET_ATM_TRANSACTIONS = 400_000

random.seed(RANDOM_SEED)


# ============================================================
# TRANSACTION TYPES
# ============================================================

TRANSACTION_TYPES = [
    ("Cash Withdrawal", 72),
    ("Cash Deposit", 8),
    ("Balance Inquiry", 10),
    ("Mini Statement", 5),
    ("PIN Change", 3),
    ("Funds Transfer", 2),
]


STATUS_WEIGHTS = [
    ("Approved", 94),
    ("Declined", 4),
    ("Failed", 1.5),
    ("Reversed", 0.5),
]


# ============================================================
# ZAMBIAN ATM LOCATIONS
# ============================================================

ATM_LOCATIONS = {
    "Lusaka": [
        "Cairo Road ATM",
        "Manda Hill ATM",
        "Arcades ATM",
        "East Park ATM",
        "Levy Mall ATM",
        "Longacres ATM",
        "Woodlands ATM",
    ],

    "Kitwe": [
        "Kitwe Main ATM",
        "Mukuba Mall ATM",
        "Chisokone ATM",
    ],

    "Ndola": [
        "Ndola Main ATM",
        "Jacaranda Mall ATM",
        "Kansenshi ATM",
    ],

    "Livingstone": [
        "Livingstone Main ATM",
        "Mosi-oa-Tunya ATM",
    ],

    "Kabwe": [
        "Kabwe Main ATM",
        "Kabwe Town Centre ATM",
    ],

    "Chingola": [
        "Chingola Main ATM",
        "Town Centre ATM",
    ],

    "Solwezi": [
        "Solwezi Main ATM",
        "Solwezi Town Centre ATM",
    ],

    "Kasama": [
        "Kasama Main ATM",
        "Town Centre ATM",
    ],

    "Mansa": [
        "Mansa Main ATM",
    ],

    "Chipata": [
        "Chipata Main ATM",
    ],

    "Choma": [
        "Choma Main ATM",
    ],

    "Mazabuka": [
        "Mazabuka Main ATM",
    ],

    "Chinsali": [
        "Chinsali Main ATM",
    ],

    "Mpika": [
        "Mpika Main ATM",
    ],

    "Mongu": [
        "Mongu Main ATM",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def weighted_choice(options):

    values = [
        item[0]
        for item in options
    ]

    weights = [
        item[1]
        for item in options
    ]

    return random.choices(
        values,
        weights=weights,
        k=1
    )[0]


def random_string(length=12):

    characters = (
        string.ascii_uppercase
        + string.digits
    )

    return "".join(
        random.choices(
            characters,
            k=length
        )
    )


def generate_atm_transaction_id():

    return (
        "ATMTRX"
        + random_string(12)
    )


def choose_transaction_datetime():

    start = datetime(
        2024,
        1,
        1
    )

    end = datetime(
        2025,
        12,
        31,
        23,
        59,
        59
    )

    total_seconds = int(
        (
            end - start
        ).total_seconds()
    )

    random_seconds = random.randint(
        0,
        total_seconds
    )

    dt = (
        start
        + timedelta(
            seconds=random_seconds
        )
    )

    # --------------------------------------------------------
    # TIME-OF-DAY BEHAVIOUR
    # --------------------------------------------------------

    hour = random.choices(
        range(24),
        weights=[
            1, 1, 1, 1, 1, 2,
            4, 7, 9, 10, 10, 9,
            9, 9, 10, 10, 11, 12,
            11, 9, 7, 5, 3, 2
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

    dt = dt.replace(
        hour=hour,
        minute=minute,
        second=second
    )

    # --------------------------------------------------------
    # MONTH-END EFFECT
    # --------------------------------------------------------

    if dt.day >= 25:

        # Higher ATM activity near month end.
        if random.random() < 0.65:

            dt = dt.replace(
                hour=random.randint(
                    7,
                    20
                )
            )

    return dt


def generate_amount(
    transaction_type
):

    if transaction_type == "Cash Withdrawal":

        amount = random.choices(
            [
                50,
                100,
                200,
                300,
                500,
                700,
                1000,
                1500,
                2000,
                3000,
                5000,
                10000
            ],
            weights=[
                2,
                7,
                15,
                16,
                23,
                10,
                10,
                5,
                4,
                3,
                2,
                1
            ],
            k=1
        )[0]

        # Occasional non-standard amount
        if random.random() < 0.04:

            amount += random.choice(
                [
                    10,
                    20,
                    50
                ]
            )

        return Decimal(
            str(amount)
        )

    if transaction_type == "Cash Deposit":

        return Decimal(
            str(
                random.randint(
                    100,
                    15000
                )
            )
        )

    if transaction_type == "Funds Transfer":

        return Decimal(
            str(
                random.randint(
                    100,
                    20000
                )
            )
        )

    return Decimal("0.00")


def generate_cash_balance():

    return Decimal(
        str(
            round(
                random.uniform(
                    50000,
                    500000
                ),
                2
            )
        )
    )


def choose_status(
    card_status
):

    status = weighted_choice(
        STATUS_WEIGHTS
    )

    # Cards that aren't active should have
    # substantially higher failure rates.

    if card_status in [
        "Blocked",
        "Expired",
        "Cancelled"
    ]:

        if random.random() < 0.80:

            status = random.choice(
                [
                    "Declined",
                    "Failed"
                ]
            )

    return status


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC ATM TRANSACTION DATA GENERATOR")
    print("=" * 70)

    print()
    print(
        f"Target ATM transactions: "
        f"{TARGET_ATM_TRANSACTIONS:,}"
    )

    print(
        f"Random seed: "
        f"{RANDOM_SEED}"
    )

    connection = None
    cursor = None

    try:

        # ====================================================
        # CONNECT
        # ====================================================

        print()
        print("Connecting to MySQL...")

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
        # LOAD CARDS
        # ====================================================

        print()
        print("Loading cards...")

        cursor.execute("""
            SELECT
                card_id,
                customer_id,
                account_id,
                status
            FROM cards
        """)

        cards = cursor.fetchall()

        print(
            f"Loaded {len(cards):,} cards."
        )

        if not cards:

            raise Exception(
                "No cards found."
            )

        # ====================================================
        # LOAD ACCOUNTS
        # ====================================================

        print("Loading accounts...")

        cursor.execute("""
            SELECT
                account_id,
                customer_id,
                branch_id,
                current_balance,
                status
            FROM accounts
        """)

        accounts = cursor.fetchall()

        print(
            f"Loaded {len(accounts):,} accounts."
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

        print(
            f"Loaded {len(branches):,} branches."
        )

        # ====================================================
        # LOAD EXISTING TRANSACTIONS ONCE
        # ====================================================

        print()
        print(
            "Loading existing transaction IDs..."
        )

        cursor.execute("""
            SELECT
                transaction_id,
                account_id,
                customer_id,
                transaction_date,
                transaction_type,
                amount,
                channel,
                branch_id,
                location,
                transaction_status
            FROM transactions
        """)

        existing_transactions = (
            cursor.fetchall()
        )

        print(
            f"Loaded "
            f"{len(existing_transactions):,} "
            f"transactions."
        )

        if not existing_transactions:

            raise Exception(
                "No transactions found. "
                "Generate transactions first."
            )

        # ====================================================
        # CREATE LOOKUPS IN MEMORY
        # ====================================================

        print()
        print(
            "Building in-memory lookups..."
        )

        account_lookup = {
            account["account_id"]: account
            for account in accounts
        }

        branch_lookup = {
            branch["branch_id"]: branch
            for branch in branches
        }

        # ----------------------------------------------------
        # Transactions grouped by account
        # ----------------------------------------------------

        transactions_by_account = (
            defaultdict(list)
        )

        for transaction in (
            existing_transactions
        ):

            transactions_by_account[
                transaction["account_id"]
            ].append(
                transaction
            )

        # ----------------------------------------------------
        # Cards grouped by account
        # ----------------------------------------------------

        cards_by_account = (
            defaultdict(list)
        )

        for card in cards:

            cards_by_account[
                card["account_id"]
            ].append(
                card
            )

        eligible_accounts = [
            account_id
            for account_id in cards_by_account
            if account_id in (
                transactions_by_account
            )
        ]

        print(
            f"Eligible accounts: "
            f"{len(eligible_accounts):,}"
        )

        # ====================================================
        # GENERATION
        # ====================================================

        print()
        print("=" * 70)
        print("GENERATING ATM TRANSACTIONS")
        print("=" * 70)

        atm_transactions = []

        type_counter = Counter()
        status_counter = Counter()
        city_counter = Counter()
        card_status_counter = Counter()

        # ----------------------------------------------------
        # ATM IDs
        # ----------------------------------------------------

        atm_ids_by_city = {}

        for city, locations in (
            ATM_LOCATIONS.items()
        ):

            atm_ids_by_city[city] = [
                f"ATM-{city[:3].upper()}-{i:03d}"
                for i in range(
                    1,
                    len(locations) + 1
                )
            ]

        # ====================================================
        # GENERATE
        # ====================================================

        while (
            len(atm_transactions)
            < TARGET_ATM_TRANSACTIONS
        ):

            # ------------------------------------------------
            # Pick an account
            # ------------------------------------------------

            account_id = random.choice(
                eligible_accounts
            )

            account = account_lookup[
                account_id
            ]

            # ------------------------------------------------
            # Pick card belonging to account
            # ------------------------------------------------

            account_cards = (
                cards_by_account[
                    account_id
                ]
            )

            card = random.choice(
                account_cards
            )

            # ------------------------------------------------
            # Pick an existing transaction
            # ------------------------------------------------

            account_transactions = (
                transactions_by_account[
                    account_id
                ]
            )

            parent_transaction = (
                random.choice(
                    account_transactions
                )
            )

            # ------------------------------------------------
            # Determine ATM transaction type
            # ------------------------------------------------

            transaction_type = weighted_choice(
                TRANSACTION_TYPES
            )

            type_counter[
                transaction_type
            ] += 1

            # ------------------------------------------------
            # Date/time
            # ------------------------------------------------

            transaction_datetime = (
                choose_transaction_datetime()
            )

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            status = choose_status(
                card["status"]
            )

            status_counter[
                status
            ] += 1

            card_status_counter[
                card["status"]
            ] += 1

            # ------------------------------------------------
            # Amount
            # ------------------------------------------------

            amount = generate_amount(
                transaction_type
            )

            # ------------------------------------------------
            # Branch / city
            # ------------------------------------------------

            branch = branch_lookup.get(
                account["branch_id"]
            )

            if branch:

                city = branch["city"]

            else:

                city = "Lusaka"

            city_counter[
                city
            ] += 1

            # ------------------------------------------------
            # ATM
            # ------------------------------------------------

            if city in atm_ids_by_city:

                atm_id = random.choice(
                    atm_ids_by_city[city]
                )

            else:

                atm_id = (
                    "ATM-ZMB-"
                    + str(
                        random.randint(
                            100,
                            999
                        )
                    )
                )

            # ------------------------------------------------
            # Location
            # ------------------------------------------------

            if city in ATM_LOCATIONS:

                location = random.choice(
                    ATM_LOCATIONS[city]
                )

            else:

                location = (
                    f"{city} ATM"
                )

            # ------------------------------------------------
            # Cash levels
            # ------------------------------------------------

            available_cash_before = (
                generate_cash_balance()
            )

            if (
                transaction_type
                == "Cash Withdrawal"
            ):

                if (
                    amount
                    <= available_cash_before
                    and status == "Approved"
                ):

                    available_cash_after = (
                        available_cash_before
                        - amount
                    )

                else:

                    available_cash_after = (
                        available_cash_before
                    )

                    if (
                        status == "Approved"
                    ):

                        status = "Declined"

            elif (
                transaction_type
                == "Cash Deposit"
            ):

                available_cash_after = (
                    available_cash_before
                    + amount
                )

            else:

                available_cash_after = (
                    available_cash_before
                )

            # ------------------------------------------------
            # Parent transaction
            # ------------------------------------------------

            transaction_id = (
                parent_transaction[
                    "transaction_id"
                ]
            )

            # ------------------------------------------------
            # ATM transaction ID
            # ------------------------------------------------

            atm_transaction_id = (
                generate_atm_transaction_id()
            )

            # ------------------------------------------------
            # Store
            # ------------------------------------------------

            atm_transactions.append(
                (
                    atm_transaction_id,
                    transaction_id,
                    atm_id,
                    card["card_id"],
                    transaction_datetime,
                    transaction_type,
                    amount,
                    location,
                    available_cash_before,
                    available_cash_after,
                    status
                )
            )

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            generated = len(
                atm_transactions
            )

            if (
                generated % 10_000
                == 0
            ):

                print(
                    f"  Generated "
                    f"{generated:,} / "
                    f"{TARGET_ATM_TRANSACTIONS:,}"
                )

        print()
        print(
            "Generation completed."
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        print()
        print("=" * 70)
        print(
            "LOCAL GENERATION VALIDATION"
        )
        print("=" * 70)

        print()
        print(
            f"ATM transactions generated: "
            f"{len(atm_transactions):,}"
        )

        print()
        print("Transaction types:")

        for transaction_type, count in (
            type_counter.most_common()
        ):

            print(
                f"  {transaction_type:<20}"
                f"{count:>9,}"
            )

        print()
        print("Transaction status:")

        for status, count in (
            status_counter.most_common()
        ):

            print(
                f"  {status:<20}"
                f"{count:>9,}"
            )

        print()
        print("ATM activity by city:")

        for city, count in (
            city_counter.most_common()
        ):

            print(
                f"  {city:<20}"
                f"{count:>9,}"
            )

        # ====================================================
        # INSERT
        # ====================================================

        print()
        print("=" * 70)
        print(
            "INSERTING INTO MYSQL"
        )
        print("=" * 70)

        insert_sql = """
            INSERT INTO atm_transactions (
                atm_transaction_id,
                transaction_id,
                atm_id,
                card_id,
                transaction_datetime,
                transaction_type,
                amount,
                location,
                available_cash_before,
                available_cash_after,
                status
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
            )
        """

        batch_size = 5_000

        for i in range(
            0,
            len(atm_transactions),
            batch_size
        ):

            batch = atm_transactions[
                i:i + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            processed = min(
                i + batch_size,
                len(atm_transactions)
            )

            if (
                processed % 25_000
                == 0
                or processed
                == len(atm_transactions)
            ):

                print(
                    f"  {processed:,} / "
                    f"{len(atm_transactions):,}"
                    f"  ("
                    f"{processed / len(atm_transactions) * 100:6.2f}"
                    f"%)"
                )

        # ====================================================
        # DATABASE VERIFICATION
        # ====================================================

        print()
        print("=" * 70)
        print(
            "DATABASE VERIFICATION"
        )
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM atm_transactions
        """)

        total = cursor.fetchone()["total"]

        print()
        print(
            f"ATM transactions currently "
            f"in database: {total:,}"
        )

        cursor.execute("""
            SELECT
                atm_transaction_id,
                transaction_id,
                atm_id,
                card_id,
                transaction_datetime,
                transaction_type,
                amount,
                location,
                status
            FROM atm_transactions
            ORDER BY RAND()
            LIMIT 10
        """)

        samples = cursor.fetchall()

        print()
        print(
            "Sample ATM transactions:"
        )

        for row in samples:

            print(
                f"{row['atm_transaction_id']} | "
                f"{row['transaction_id']} | "
                f"{row['atm_id']} | "
                f"{row['card_id']} | "
                f"{row['transaction_type']} | "
                f"K{row['amount']:,.2f} | "
                f"{row['location']} | "
                f"{row['status']}"
            )

        print()
        print(
            "✓ ATM transaction table "
            "successfully populated."
        )

    except Error as e:

        print()
        print(
            f"MySQL Error: {e}"
        )

    except Exception as e:

        print()
        print(
            f"Unexpected Error: {e}"
        )

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):

            connection.close()

        print()
        print("=" * 70)
        print(
            "KWACHA BANK ATM TRANSACTION "
            "GENERATION FINISHED"
        )
        print("=" * 70)


if __name__ == "__main__":
    main()