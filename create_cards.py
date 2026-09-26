import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import random


# ============================================================
# KWACHA BANK
# SYNTHETIC CARD DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)

TODAY = date(2026, 8, 13)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_age(dob):

    age = TODAY.year - dob.year

    if (TODAY.month, TODAY.day) < (dob.month, dob.day):
        age -= 1

    return age


def to_float(value, default=0.0):

    if value is None:
        return default

    return float(value)


def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(value, maximum)
    )


# ============================================================
# CARD ELIGIBILITY
# ============================================================

def is_card_eligible(account):

    account_type = account["account_type_id"]
    status = account["status"]

    # Closed and frozen accounts should not normally
    # receive new cards.
    if status in ["Closed", "Frozen"]:
        return False

    # Fixed deposit accounts are not transactional accounts.
    if account_type == "AT009":
        return False

    return account_type in [
        "AT001",  # Basic Savings
        "AT002",  # Premium Savings
        "AT003",  # Current
        "AT004",  # Student
        "AT005",  # Youth
        "AT006",  # Salary
        "AT007",  # Business Savings
        "AT008",  # Business Current
        "AT010"   # Premier
    ]


# ============================================================
# CARD PROBABILITY
# ============================================================

def card_probability(account, customer):

    account_type = account["account_type_id"]

    segment = customer["customer_segment"]

    employment = customer["employment_status"]

    age = calculate_age(
        customer["date_of_birth"]
    )

    probability = 0.0

    if account_type == "AT001":
        probability = 0.72

    elif account_type == "AT002":
        probability = 0.85

    elif account_type == "AT003":
        probability = 0.88

    elif account_type == "AT004":
        probability = 0.70

    elif account_type == "AT005":
        probability = 0.75

    elif account_type == "AT006":
        probability = 0.94

    elif account_type == "AT007":
        probability = 0.80

    elif account_type == "AT008":
        probability = 0.90

    elif account_type == "AT010":
        probability = 0.96

    # Customer segment effects

    if segment == "Affluent":
        probability += 0.02

    elif segment == "Mass Affluent":
        probability += 0.02

    elif segment == "Youth":
        probability += 0.03

    elif segment == "Entry Level":
        probability -= 0.05

    # Employment effects

    if employment == "Employed":
        probability += 0.03

    elif employment == "Student":
        probability += 0.02

    elif employment == "Unemployed":
        probability -= 0.08

    # Young customers

    if age < 18:
        return 0.0

    if age < 21:
        probability -= 0.05

    return clamp(
        probability,
        0.05,
        0.98
    )


# ============================================================
# CARD TYPE
# ============================================================

def choose_card_type(customer, account):

    segment = customer["customer_segment"]

    account_type = account["account_type_id"]

    if account_type in ["AT007", "AT008"]:

        return random.choices(
            [
                "Business Debit",
                "Business Premium Debit"
            ],
            weights=[
                75,
                25
            ],
            k=1
        )[0]

    if account_type == "AT010":

        return random.choices(
            [
                "Premium Debit",
                "Platinum Debit"
            ],
            weights=[
                45,
                55
            ],
            k=1
        )[0]

    if account_type in ["AT004", "AT005"]:

        return "Youth Debit"

    if segment == "Affluent":

        return random.choices(
            [
                "Premium Debit",
                "Platinum Debit",
                "Standard Debit"
            ],
            weights=[
                40,
                45,
                15
            ],
            k=1
        )[0]

    if segment == "Mass Affluent":

        return random.choices(
            [
                "Premium Debit",
                "Standard Debit"
            ],
            weights=[
                35,
                65
            ],
            k=1
        )[0]

    return random.choices(
        [
            "Standard Debit",
            "Premium Debit"
        ],
        weights=[
            85,
            15
        ],
        k=1
    )[0]


# ============================================================
# ISSUE DATE
# ============================================================

def generate_issue_date(account):

    open_date = account["open_date"]

    # Safety check
    if open_date >= TODAY:
        return TODAY

    available_days = (
        TODAY - open_date
    ).days

    # Account opened today or yesterday
    if available_days <= 0:
        return open_date

    # Accounts opened within the last 90 days
    if available_days <= 90:

        delay = random.randint(
            0,
            available_days
        )

        return (
            open_date
            +
            timedelta(days=delay)
        )

    # Accounts opened within the last year
    if available_days <= 365:

        delay = random.randint(
            0,
            available_days
        )

        return (
            open_date
            +
            timedelta(days=delay)
        )

    # Accounts older than one year.
    #
    # Most cards are issued within the first year,
    # but some are issued later.
    delay = random.choices(
        [
            random.randint(0, 90),
            random.randint(91, 365),
            random.randint(366, available_days)
        ],
        weights=[
            55,
            30,
            15
        ],
        k=1
    )[0]

    return (
        open_date
        +
        timedelta(days=delay)
    )


# ============================================================
# EXPIRY DATE
# ============================================================

def generate_expiry_date(issue_date):

    years = random.choice(
        [3, 4, 5]
    )

    # Avoid February 29 problems.
    day = min(
        issue_date.day,
        28
    )

    return date(
        issue_date.year + years,
        issue_date.month,
        day
    )


# ============================================================
# DAILY CARD LIMIT
# ============================================================

def generate_daily_limit(customer, card_type):

    segment = customer["customer_segment"]

    income = to_float(
        customer["monthly_income"]
    )

    if card_type == "Youth Debit":

        base = random.uniform(
            1500,
            5000
        )

    elif card_type == "Standard Debit":

        base = random.uniform(
            5000,
            15000
        )

    elif card_type == "Premium Debit":

        base = random.uniform(
            15000,
            50000
        )

    elif card_type == "Platinum Debit":

        base = random.uniform(
            30000,
            100000
        )

    elif card_type == "Business Debit":

        base = random.uniform(
            20000,
            100000
        )

    elif card_type == "Business Premium Debit":

        base = random.uniform(
            50000,
            250000
        )

    else:

        base = random.uniform(
            5000,
            15000
        )

    # Income should influence limits.

    if income > 0:

        income_based_limit = (
            income
            *
            random.uniform(
                0.5,
                3.0
            )
        )

        base = (
            base * 0.6
            +
            income_based_limit * 0.4
        )

    # Segment influence

    if segment == "Affluent":

        base *= random.uniform(
            1.3,
            2.0
        )

    elif segment == "Mass Affluent":

        base *= random.uniform(
            1.1,
            1.5
        )

    elif segment == "Youth":

        base *= random.uniform(
            0.5,
            0.8
        )

    return round(
        clamp(
            base,
            1000,
            500000
        ),
        2
    )


# ============================================================
# INTERNATIONAL TRANSACTIONS
# ============================================================

def determine_international(customer, card_type):

    segment = customer["customer_segment"]

    if card_type in [
        "Platinum Debit",
        "Business Premium Debit"
    ]:

        return random.random() < 0.75

    if segment == "Affluent":

        return random.random() < 0.70

    if segment == "Mass Affluent":

        return random.random() < 0.45

    return random.random() < 0.12


# ============================================================
# CARD STATUS
# ============================================================

def determine_status(
    issue_date,
    expiry_date,
    account_status
):

    # Expired cards
    if expiry_date < TODAY:

        return random.choices(
            [
                "Expired",
                "Cancelled"
            ],
            weights=[
                85,
                15
            ],
            k=1
        )[0]

    # Account status effects

    if account_status == "Closed":
        return "Cancelled"

    if account_status == "Frozen":
        return "Blocked"

    # Current cards

    return random.choices(
        [
            "Active",
            "Blocked",
            "Cancelled"
        ],
        weights=[
            96,
            2,
            2
        ],
        k=1
    )[0]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC CARD DATA GENERATOR")
    print("=" * 70)

    print(
        f"\nRandom seed: {RANDOM_SEED}"
    )

    connection = None
    cursor = None

    try:

        # ====================================================
        # CONNECT
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
                date_of_birth,
                employment_status,
                monthly_income,
                customer_segment
            FROM customers
        """)

        customers = cursor.fetchall()

        customer_lookup = {
            customer["customer_id"]: customer
            for customer in customers
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
                open_date,
                status
            FROM accounts
        """)

        accounts = cursor.fetchall()

        print(
            f"Loaded {len(accounts):,} accounts."
        )

        # ====================================================
        # GENERATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("GENERATING CARDS")
        print("=" * 70)

        generated_cards = []

        card_sequence = 1

        accounts_considered = 0
        eligible_accounts = 0
        accounts_with_cards = 0
        accounts_without_cards = 0

        card_type_counts = {}
        status_counts = {}

        for index, account in enumerate(
            accounts,
            start=1
        ):

            accounts_considered += 1

            customer = customer_lookup.get(
                account["customer_id"]
            )

            if customer is None:
                continue

            if not is_card_eligible(
                account
            ):
                continue

            eligible_accounts += 1

            probability = card_probability(
                account,
                customer
            )

            # No card
            if random.random() > probability:

                accounts_without_cards += 1

                continue

            accounts_with_cards += 1

            # Usually one card.
            # Small probability of two cards.
            number_of_cards = 1

            if random.random() < 0.025:
                number_of_cards = 2

            for _ in range(
                number_of_cards
            ):

                card_type = choose_card_type(
                    customer,
                    account
                )

                issue_date = generate_issue_date(
                    account
                )

                expiry_date = generate_expiry_date(
                    issue_date
                )

                daily_limit = generate_daily_limit(
                    customer,
                    card_type
                )

                international_enabled = (
                    determine_international(
                        customer,
                        card_type
                    )
                )

                status = determine_status(
                    issue_date,
                    expiry_date,
                    account["status"]
                )

                card_id = (
                    f"CARD{card_sequence:010d}"
                )

                generated_cards.append(
                    (
                        card_id,
                        customer["customer_id"],
                        account["account_id"],
                        card_type,
                        issue_date,
                        expiry_date,
                        status,
                        daily_limit,
                        international_enabled
                    )
                )

                card_sequence += 1

                card_type_counts[
                    card_type
                ] = (
                    card_type_counts.get(
                        card_type,
                        0
                    ) + 1
                )

                status_counts[
                    status
                ] = (
                    status_counts.get(
                        status,
                        0
                    ) + 1
                )

            if index % 1000 == 0:

                print(
                    f"  Processed "
                    f"{index:,} / "
                    f"{len(accounts):,} accounts"
                )

        # ====================================================
        # VALIDATION
        # ====================================================

        print("\nGeneration completed.")

        print("\n")
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        print(
            f"\nAccounts processed: "
            f"{accounts_considered:,}"
        )

        print(
            f"Card-eligible accounts: "
            f"{eligible_accounts:,}"
        )

        print(
            f"Accounts with cards: "
            f"{accounts_with_cards:,}"
        )

        print(
            f"Accounts without cards: "
            f"{accounts_without_cards:,}"
        )

        print(
            f"Total cards generated: "
            f"{len(generated_cards):,}"
        )

        print("\nCard types:")

        for card_type, count in sorted(
            card_type_counts.items()
        ):

            print(
                f"  {card_type:<25}"
                f"{count:,}"
            )

        print("\nCard status:")

        for status, count in sorted(
            status_counts.items()
        ):

            print(
                f"  {status:<12}"
                f"{count:,}"
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
            INSERT INTO cards (
                card_id,
                customer_id,
                account_id,
                card_type,
                issue_date,
                expiry_date,
                status,
                daily_limit,
                international_enabled
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        batch_size = 1000

        total = len(
            generated_cards
        )

        for start in range(
            0,
            total,
            batch_size
        ):

            batch = generated_cards[
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

            print(
                f"  {end:,} / "
                f"{total:,} "
                f"({percentage:6.2f}%)"
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
            FROM cards
        """)

        card_count = cursor.fetchone()[0]

        print(
            f"\nCards currently in database: "
            f"{card_count:,}"
        )

        cursor.execute("""
            SELECT AVG(daily_limit)
            FROM cards
        """)

        average_limit = (
            cursor.fetchone()[0]
        )

        print(
            f"Average daily card limit: "
            f"K{float(average_limit):,.2f}"
        )

        cursor.execute("""
            SELECT COUNT(DISTINCT customer_id)
            FROM cards
        """)

        customers_with_cards = (
            cursor.fetchone()[0]
        )

        print(
            f"Customers with cards: "
            f"{customers_with_cards:,}"
        )

        # ====================================================
        # SAMPLE DATA
        # ====================================================

        cursor.execute("""
            SELECT
                ca.card_id,
                c.first_name,
                c.last_name,
                a.account_id,
                ca.card_type,
                ca.issue_date,
                ca.expiry_date,
                ca.status,
                ca.daily_limit
            FROM cards ca

            JOIN customers c
                ON ca.customer_id =
                   c.customer_id

            JOIN accounts a
                ON ca.account_id =
                   a.account_id

            ORDER BY ca.card_id

            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample cards:\n")

        for row in rows:

            print(
                f"{row['card_id']} | "
                f"{row['first_name']} "
                f"{row['last_name']} | "
                f"{row['account_id']} | "
                f"{row['card_type']} | "
                f"{row['issue_date']} | "
                f"{row['expiry_date']} | "
                f"{row['status']} | "
                f"K{float(row['daily_limit']):,.2f}"
            )

        print(
            "\n✓ Card table successfully populated."
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
    print("KWACHA BANK CARD GENERATION FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()