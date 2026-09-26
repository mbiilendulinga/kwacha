import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import random


# ============================================================
# KWACHA BANK
# SYNTHETIC ACCOUNT DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)


# ============================================================
# SETTINGS
# ============================================================

MAX_ACCOUNTS_PER_CUSTOMER = 4

TODAY = date(2026, 8, 13)


# ============================================================
# GLOBAL ACCOUNT TYPES
# ============================================================

ACCOUNT_TYPES = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def to_float(value, default=0.0):
    """
    Safely convert MySQL Decimal / None / numeric values
    into Python float.

    This prevents Decimal + float errors.
    """

    if value is None:
        return default

    return float(value)


def calculate_age(dob):

    age = TODAY.year - dob.year

    if (TODAY.month, TODAY.day) < (dob.month, dob.day):
        age -= 1

    return age


def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(value, maximum)
    )


# ============================================================
# BRANCH SELECTION
# ============================================================

def choose_branch(customer, branches):

    province = customer["province"]

    same_province = [
        branch
        for branch in branches
        if branch["province"] == province
    ]

    # 90% chance of customer's home province
    if same_province and random.random() < 0.90:
        return random.choice(same_province)

    # 10% chance of another province
    return random.choice(branches)


# ============================================================
# NUMBER OF ACCOUNTS
# ============================================================

def determine_account_count(customer):

    age = calculate_age(
        customer["date_of_birth"]
    )

    income = to_float(
        customer["monthly_income"]
    )

    segment = customer["customer_segment"]

    employment = customer["employment_status"]

    probability = 0.10

    # --------------------------------------------------------
    # Income
    # --------------------------------------------------------

    if income >= 30000:

        probability += 0.25

    elif income >= 15000:

        probability += 0.15

    elif income >= 8000:

        probability += 0.08

    # --------------------------------------------------------
    # Customer segment
    # --------------------------------------------------------

    if segment == "Affluent":

        probability += 0.40

    elif segment == "Mass Affluent":

        probability += 0.25

    elif segment == "Business":

        probability += 0.20

    elif segment == "Mass Market":

        probability += 0.05

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    if employment == "Self-employed":

        probability += 0.15

    elif employment == "Employed":

        probability += 0.05

    # --------------------------------------------------------
    # Age
    # --------------------------------------------------------

    if age >= 40:

        probability += 0.10

    if age < 25:

        probability -= 0.08

    probability = clamp(
        probability,
        0.03,
        0.80
    )

    # --------------------------------------------------------
    # Most customers get at least one account
    # --------------------------------------------------------

    if random.random() < 0.97:

        count = 1

        if random.random() < probability:
            count += 1

        if random.random() < probability * 0.35:
            count += 1

        if random.random() < probability * 0.12:
            count += 1

        return min(
            count,
            MAX_ACCOUNTS_PER_CUSTOMER
        )

    return 0


# ============================================================
# ACCOUNT TYPE
# ============================================================

def choose_account_type(
    customer,
    existing_types
):

    age = calculate_age(
        customer["date_of_birth"]
    )

    employment = customer["employment_status"]

    segment = customer["customer_segment"]

    income = to_float(
        customer["monthly_income"]
    )

    available = [
        account
        for account in ACCOUNT_TYPES
        if account["account_type_id"]
        not in existing_types
    ]

    if not available:

        available = ACCOUNT_TYPES

    weighted_accounts = []

    for account in available:

        account_id = account[
            "account_type_id"
        ]

        weight = 1.0

        # ----------------------------------------------------
        # BASIC SAVINGS
        # ----------------------------------------------------

        if account_id == "AT001":

            weight = 10

        # ----------------------------------------------------
        # PREMIUM SAVINGS
        # ----------------------------------------------------

        elif account_id == "AT002":

            if income >= 20000:
                weight = 8

            elif segment in [
                "Mass Affluent",
                "Affluent"
            ]:
                weight = 10

            else:
                weight = 1

        # ----------------------------------------------------
        # CURRENT
        # ----------------------------------------------------

        elif account_id == "AT003":

            if employment in [
                "Employed",
                "Self-employed"
            ]:
                weight = 8

            else:
                weight = 2

        # ----------------------------------------------------
        # STUDENT
        # ----------------------------------------------------

        elif account_id == "AT004":

            if employment == "Student":
                weight = 30

            else:
                weight = 0.3

        # ----------------------------------------------------
        # YOUTH
        # ----------------------------------------------------

        elif account_id == "AT005":

            if age < 30:
                weight = 15

            else:
                weight = 0.5

        # ----------------------------------------------------
        # SALARY
        # ----------------------------------------------------

        elif account_id == "AT006":

            if employment == "Employed":
                weight = 20

            else:
                weight = 0.5

        # ----------------------------------------------------
        # BUSINESS
        # ----------------------------------------------------

        elif account_id == "AT007":

            if employment == "Self-employed":
                weight = 15

            elif segment == "Business":
                weight = 20

            else:
                weight = 0.3

        # ----------------------------------------------------
        # SME CURRENT
        # ----------------------------------------------------

        elif account_id == "AT008":

            if segment == "Business":
                weight = 15

            elif employment == "Self-employed":
                weight = 12

            else:
                weight = 0.2

        # ----------------------------------------------------
        # FIXED DEPOSIT
        # ----------------------------------------------------

        elif account_id == "AT009":

            if segment in [
                "Affluent",
                "Mass Affluent"
            ]:

                weight = 10

            elif income >= 30000:

                weight = 6

            else:

                weight = 0.5

        # ----------------------------------------------------
        # PREMIER
        # ----------------------------------------------------

        elif account_id == "AT010":

            if segment == "Affluent":

                weight = 20

            elif segment == "Mass Affluent":

                weight = 8

            elif income >= 40000:

                weight = 10

            else:

                weight = 0.1

        weighted_accounts.append(
            (
                account,
                weight
            )
        )

    accounts = [
        item[0]
        for item in weighted_accounts
    ]

    weights = [
        item[1]
        for item in weighted_accounts
    ]

    return random.choices(
        accounts,
        weights=weights,
        k=1
    )[0]


# ============================================================
# ACCOUNT OPEN DATE
# ============================================================

def generate_open_date(customer):

    customer_since = customer[
        "customer_since"
    ]

    if customer_since >= TODAY:

        return TODAY

    available_days = (
        TODAY - customer_since
    ).days

    return (
        customer_since
        +
        timedelta(
            days=random.randint(
                0,
                max(0, available_days)
            )
        )
    )


# ============================================================
# BALANCE GENERATION
# ============================================================

def generate_balance(
    customer,
    account_type
):

    income = to_float(
        customer["monthly_income"]
    )

    segment = customer[
        "customer_segment"
    ]

    account_id = account_type[
        "account_type_id"
    ]

    # --------------------------------------------------------
    # Base balance
    # --------------------------------------------------------

    if income <= 0:

        base = random.uniform(
            0,
            1500
        )

    else:

        multiplier = random.uniform(
            0.15,
            2.5
        )

        base = income * multiplier

    # --------------------------------------------------------
    # Segment behaviour
    # --------------------------------------------------------

    if segment == "Affluent":

        base *= random.uniform(
            2.0,
            6.0
        )

    elif segment == "Mass Affluent":

        base *= random.uniform(
            1.2,
            3.0
        )

    elif segment == "Business":

        base *= random.uniform(
            1.3,
            4.0
        )

    elif segment == "Youth":

        base *= random.uniform(
            0.25,
            0.8
        )

    elif segment == "Entry Level":

        base *= random.uniform(
            0.30,
            0.90
        )

    # --------------------------------------------------------
    # Account type
    # --------------------------------------------------------

    if account_id == "AT009":

        base = max(
            base,
            random.uniform(
                10000,
                150000
            )
        )

    elif account_id == "AT010":

        base = max(
            base,
            random.uniform(
                25000,
                200000
            )
        )

    elif account_id in [
        "AT007",
        "AT008"
    ]:

        base = max(
            base,
            random.uniform(
                5000,
                100000
            )
        )

    # --------------------------------------------------------
    # Low balance customers
    # --------------------------------------------------------

    if random.random() < 0.12:

        base *= random.uniform(
            0.01,
            0.20
        )

    # --------------------------------------------------------
    # High-value outliers
    # --------------------------------------------------------

    if random.random() < 0.025:

        base *= random.uniform(
            3,
            12
        )

    return round(
        clamp(
            base,
            0,
            5000000
        ),
        2
    )


# ============================================================
# ACCOUNT STATUS
# ============================================================

def determine_status():

    random_number = random.random()

    if random_number < 0.025:

        return "Closed"

    elif random_number < 0.033:

        return "Frozen"

    elif random_number < 0.078:

        return "Dormant"

    return "Active"


# ============================================================
# CLOSE DATE
# ============================================================

def generate_close_date(
    open_date,
    status
):

    if status != "Closed":

        return None

    if open_date >= TODAY:

        return None

    available_days = (
        TODAY - open_date
    ).days

    if available_days < 30:

        return None

    return (
        open_date
        +
        timedelta(
            days=random.randint(
                30,
                available_days
            )
        )
    )


# ============================================================
# INTEREST RATE
# ============================================================

def generate_interest_rate(
    account_type
):

    base = to_float(
        account_type["interest_rate"]
    )

    variation = random.uniform(
        -0.25,
        0.25
    )

    return round(
        max(
            0,
            base + variation
        ),
        2
    )


# ============================================================
# OVERDRAFT
# ============================================================

def generate_overdraft(
    customer,
    account_type
):

    account_id = account_type[
        "account_type_id"
    ]

    employment = customer[
        "employment_status"
    ]

    income = to_float(
        customer["monthly_income"]
    )

    eligible_types = [
        "AT003",
        "AT006",
        "AT007",
        "AT008"
    ]

    if account_id not in eligible_types:

        return 0

    if employment not in [
        "Employed",
        "Self-employed"
    ]:

        return 0

    if random.random() > 0.30:

        return 0

    if income <= 0:

        return 0

    limit = (
        income
        *
        random.uniform(
            0.25,
            1.5
        )
    )

    return round(
        clamp(
            limit,
            500,
            100000
        ),
        2
    )


# ============================================================
# MAIN
# ============================================================

def main():

    global ACCOUNT_TYPES

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC ACCOUNT DATA GENERATOR")
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
                date_of_birth,
                province,
                employment_status,
                monthly_income,
                customer_since,
                customer_segment
            FROM customers
            ORDER BY customer_id
        """)

        customers = cursor.fetchall()

        print(
            f"Loaded {len(customers):,} customers."
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
                city,
                branch_type
            FROM branches
        """)

        branches = cursor.fetchall()

        print(
            f"Loaded {len(branches):,} branches."
        )

        # ====================================================
        # LOAD ACCOUNT TYPES
        # ====================================================

        print("Loading account types...")

        cursor.execute("""
            SELECT
                account_type_id,
                account_name,
                category,
                minimum_balance,
                monthly_fee,
                interest_rate
            FROM account_types
        """)

        ACCOUNT_TYPES = cursor.fetchall()

        print(
            f"Loaded {len(ACCOUNT_TYPES):,} "
            f"account types."
        )

        # ====================================================
        # GENERATE
        # ====================================================

        print("\n")
        print("=" * 70)
        print("GENERATING ACCOUNTS")
        print("=" * 70)

        generated_accounts = []

        account_sequence = 1

        customers_with_accounts = 0
        customers_without_accounts = 0

        account_type_counts = {}
        status_counts = {}

        for index, customer in enumerate(
            customers,
            start=1
        ):

            number_of_accounts = (
                determine_account_count(
                    customer
                )
            )

            if number_of_accounts == 0:

                customers_without_accounts += 1

                continue

            customers_with_accounts += 1

            existing_types = set()

            for _ in range(
                number_of_accounts
            ):

                account_type = (
                    choose_account_type(
                        customer,
                        existing_types
                    )
                )

                existing_types.add(
                    account_type[
                        "account_type_id"
                    ]
                )

                branch = choose_branch(
                    customer,
                    branches
                )

                open_date = (
                    generate_open_date(
                        customer
                    )
                )

                balance = (
                    generate_balance(
                        customer,
                        account_type
                    )
                )

                status = (
                    determine_status()
                )

                close_date = (
                    generate_close_date(
                        open_date,
                        status
                    )
                )

                interest_rate = (
                    generate_interest_rate(
                        account_type
                    )
                )

                overdraft_limit = (
                    generate_overdraft(
                        customer,
                        account_type
                    )
                )

                account_id = (
                    f"ACC{account_sequence:010d}"
                )

                # ------------------------------------------------
                # Generate unique account number
                # ------------------------------------------------

                account_number = None

                while account_number is None:

                    candidate = (
                        "KW"
                        +
                        str(
                            random.randint(
                                10,
                                99
                            )
                        )
                        +
                        str(
                            random.randint(
                                10000000,
                                99999999
                            )
                        )
                    )

                    account_number = candidate

                # ------------------------------------------------
                # Available balance
                # ------------------------------------------------

                available_balance = (
                    balance
                    +
                    overdraft_limit
                )

                if status == "Closed":

                    available_balance = 0

                # ------------------------------------------------
                # Small amount of intentionally messy data
                # ------------------------------------------------

                if random.random() < 0.003:

                    available_balance = round(
                        balance
                        *
                        random.uniform(
                            0.95,
                            1.05
                        ),
                        2
                    )

                generated_accounts.append(
                    (
                        account_id,
                        customer["customer_id"],
                        account_type[
                            "account_type_id"
                        ],
                        branch["branch_id"],
                        account_number,
                        "ZMW",
                        open_date,
                        close_date,
                        balance,
                        available_balance,
                        status,
                        interest_rate,
                        overdraft_limit
                    )
                )

                account_sequence += 1

                # Statistics

                account_type_id = (
                    account_type[
                        "account_type_id"
                    ]
                )

                account_type_counts[
                    account_type_id
                ] = (
                    account_type_counts.get(
                        account_type_id,
                        0
                    )
                    +
                    1
                )

                status_counts[
                    status
                ] = (
                    status_counts.get(
                        status,
                        0
                    )
                    +
                    1
                )

            # Progress

            if index % 1000 == 0:

                print(
                    f"  Processed "
                    f"{index:,} / "
                    f"{len(customers):,} "
                    f"customers"
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
            f"\nCustomers processed: "
            f"{len(customers):,}"
        )

        print(
            f"Customers with accounts: "
            f"{customers_with_accounts:,}"
        )

        print(
            f"Customers without accounts: "
            f"{customers_without_accounts:,}"
        )

        print(
            f"Total accounts generated: "
            f"{len(generated_accounts):,}"
        )

        average_accounts = (
            len(generated_accounts)
            /
            len(customers)
        )

        print(
            f"Average accounts per customer: "
            f"{average_accounts:.2f}"
        )

        print("\nAccount types:")

        for account_type_id, count in sorted(
            account_type_counts.items()
        ):

            print(
                f"  {account_type_id}: "
                f"{count:,}"
            )

        print("\nAccount status:")

        for status, count in sorted(
            status_counts.items()
        ):

            print(
                f"  {status:<10} "
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
            INSERT INTO accounts (
                account_id,
                customer_id,
                account_type_id,
                branch_id,
                account_number,
                currency,
                open_date,
                close_date,
                current_balance,
                available_balance,
                status,
                interest_rate,
                overdraft_limit
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        batch_size = 1000

        for start in range(
            0,
            len(generated_accounts),
            batch_size
        ):

            batch = generated_accounts[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            end = min(
                start + batch_size,
                len(generated_accounts)
            )

            percentage = (
                end
                /
                len(generated_accounts)
            ) * 100

            print(
                f"  {end:,} / "
                f"{len(generated_accounts):,} "
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
            FROM accounts
        """)

        account_count = cursor.fetchone()[0]

        print(
            f"\nAccounts currently in database: "
            f"{account_count:,}"
        )

        cursor.execute("""
            SELECT
                AVG(current_balance)
            FROM accounts
        """)

        average_balance = (
            cursor.fetchone()[0]
        )

        print(
            f"Average current balance: "
            f"K{float(average_balance):,.2f}"
        )

        cursor.execute("""
            SELECT
                SUM(current_balance)
            FROM accounts
        """)

        total_balance = (
            cursor.fetchone()[0]
        )

        print(
            f"Total balances held: "
            f"K{float(total_balance):,.2f}"
        )

        # ====================================================
        # SAMPLE
        # ====================================================

        cursor.execute("""
            SELECT
                a.account_id,
                a.customer_id,
                c.first_name,
                c.last_name,
                at.account_name,
                b.branch_name,
                a.current_balance,
                a.status
            FROM accounts a

            JOIN customers c
                ON a.customer_id =
                   c.customer_id

            JOIN account_types at
                ON a.account_type_id =
                   at.account_type_id

            JOIN branches b
                ON a.branch_id =
                   b.branch_id

            ORDER BY a.account_id

            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample accounts:\n")

        for row in rows:

            print(
                f"{row[0]} | "
                f"{row[1]} | "
                f"{row[2]} {row[3]} | "
                f"{row[4]} | "
                f"{row[5]} | "
                f"K{float(row[6]):,.2f} | "
                f"{row[7]}"
            )

        print(
            "\n✓ Account table successfully populated."
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
    print("KWACHA BANK ACCOUNT GENERATION FINISHED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()