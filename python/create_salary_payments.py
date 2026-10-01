import mysql.connector
from mysql.connector import Error
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
import random
import calendar
import string


# ============================================================
# KWACHA BANK
# SYNTHETIC SALARY PAYMENT DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

# Generate one year of salary history
START_YEAR = 2025
START_MONTH = 1

END_YEAR = 2025
END_MONTH = 12


random.seed(RANDOM_SEED)


# ============================================================
# CONFIGURATION
# ============================================================

EMPLOYED_PROBABILITY = 0.94
SELF_EMPLOYED_PROBABILITY = 0.18

# Small chance of a missed salary payment
MISSED_PAYMENT_PROBABILITY = 0.025

# Small chance of employer-name inconsistency
EMPLOYER_VARIATION_PROBABILITY = 0.035

# Small chance payment arrives unusually early/late
UNUSUAL_PAYMENT_DATE_PROBABILITY = 0.08


# ============================================================
# ZAMBIAN EMPLOYER NAMES
# ============================================================

EMPLOYER_NAMES = {

    "Government": [
        "Government of Zambia",
        "Ministry of Education",
        "Ministry of Health",
        "Zambia Revenue Authority",
        "National Pension Scheme Authority",
        "Bank of Zambia",
        "Zambia Police Service",
        "Zambia Defence Force",
        "Zambia National Broadcasting Corporation",
        "University of Zambia",
        "Copperbelt University",
    ],

    "Banking": [
        "Kwacha Bank",
        "Zambia Commercial Bank",
        "National Savings and Credit Bank",
        "Stanbic Bank Zambia",
        "Absa Bank Zambia",
        "First National Bank Zambia",
        "Standard Chartered Bank Zambia",
    ],

    "Mining": [
        "Konkola Copper Mines",
        "Mopani Copper Mines",
        "First Quantum Minerals",
        "Barrick Lumwana Mining",
        "Chambishi Copper Smelter",
        "Mopani Mining",
    ],

    "Telecommunications": [
        "MTN Zambia",
        "Airtel Zambia",
        "Zamtel",
    ],

    "Education": [
        "University of Zambia",
        "Copperbelt University",
        "University Teaching Hospital School of Nursing",
        "Lusaka International Community School",
        "David Kaunda Technical High School",
    ],

    "Healthcare": [
        "University Teaching Hospital",
        "Ndola Teaching Hospital",
        "Levy Mwanawasa University Teaching Hospital",
        "Medland Hospital",
        "Coptic Hospital",
    ],

    "Retail": [
        "Shoprite Zambia",
        "Pick n Pay Zambia",
        "Game Stores Zambia",
        "Choppies Zambia",
        "Hungry Lion Zambia",
    ],

    "Manufacturing": [
        "Trade Kings Zambia",
        "Dangote Industries Zambia",
        "Lafarge Zambia",
        "Zambeef Products",
        "National Milling Corporation",
    ],

    "Professional": [
        "PricewaterhouseCoopers Zambia",
        "Deloitte Zambia",
        "KPMG Zambia",
        "Ernst & Young Zambia",
    ],

    "Other": [
        "Zambia Sugar",
        "Zambezi Airlines",
        "Zambia National Commercial Bank",
        "Madison General Insurance",
        "Professional Insurance Corporation Zambia",
        "Zambia State Insurance Corporation",
    ]
}


EMPLOYER_WEIGHTS = {
    "Government": 0.28,
    "Banking": 0.08,
    "Mining": 0.10,
    "Telecommunications": 0.05,
    "Education": 0.08,
    "Healthcare": 0.08,
    "Retail": 0.08,
    "Manufacturing": 0.07,
    "Professional": 0.06,
    "Other": 0.12
}


# ============================================================
# CONNECTION
# ============================================================

def connect_database():

    try:

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

        return connection

    except Error as e:

        print(f"MySQL connection error: {e}")

        return None


# ============================================================
# RANDOM SALARY PAYMENT ID
# ============================================================

def generate_salary_payment_id(existing_ids):

    characters = string.ascii_uppercase + string.digits

    while True:

        random_part = "".join(
            random.choices(
                characters,
                k=8
            )
        )

        payment_id = f"SAL-{random_part}"

        if payment_id not in existing_ids:

            existing_ids.add(payment_id)

            return payment_id


# ============================================================
# MONTH RANGE
# ============================================================

def generate_months():

    months = []

    current_year = START_YEAR
    current_month = START_MONTH

    while True:

        months.append(
            date(
                current_year,
                current_month,
                1
            )
        )

        if (
            current_year == END_YEAR
            and current_month == END_MONTH
        ):
            break

        current_month += 1

        if current_month > 12:

            current_month = 1
            current_year += 1

    return months


# ============================================================
# EMPLOYER CATEGORY
# ============================================================

def choose_employer_category():

    categories = list(
        EMPLOYER_WEIGHTS.keys()
    )

    weights = list(
        EMPLOYER_WEIGHTS.values()
    )

    return random.choices(
        categories,
        weights=weights,
        k=1
    )[0]


# ============================================================
# EMPLOYER NAME
# ============================================================

def generate_employer():

    category = choose_employer_category()

    employer = random.choice(
        EMPLOYER_NAMES[category]
    )

    return employer


# ============================================================
# EMPLOYER NAME MESSINESS
# ============================================================

def make_messy_employer_name(employer):

    variations = [

        employer.upper(),

        employer.lower(),

        employer.replace(
            "Zambia",
            "ZAMBIA"
        ),

        employer.replace(
            "Limited",
            "Ltd"
        ),

        employer.replace(
            "Limited",
            "LTD"
        ),

        employer.replace(
            "Corporation",
            "Corp."
        ),

        employer + " ",

        " " + employer,

    ]

    return random.choice(
        variations
    )


# ============================================================
# SALARY VARIATION
# ============================================================

def generate_salary_amount(
    monthly_income,
    employment_status
):

    if monthly_income is None:

        return None

    income = Decimal(
        str(monthly_income)
    )

    # Salary payment should generally resemble
    # the customer's recorded monthly income.

    variation = Decimal(
        str(
            random.uniform(
                -0.025,
                0.025
            )
        )
    )

    amount = income * (
        Decimal("1.00")
        + variation
    )

    # Occasional bonus / allowance
    if random.random() < 0.07:

        bonus = income * Decimal(
            str(
                random.uniform(
                    0.05,
                    0.20
                )
            )
        )

        amount += bonus

    # Round to nearest ngwee
    amount = amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return amount


# ============================================================
# PAYMENT DATE
# ============================================================

def generate_payment_date(
    month,
    customer_since
):

    year = month.year
    month_number = month.month

    last_day = calendar.monthrange(
        year,
        month_number
    )[1]

    # Normal salary dates:
    # 25th - 30th of the month
    payment_day = random.randint(
        25,
        min(30, last_day)
    )

    # Some employers pay around month-end
    if random.random() < 0.35:

        payment_day = last_day

    # Occasionally pay earlier/later
    if random.random() < UNUSUAL_PAYMENT_DATE_PROBABILITY:

        shift = random.choice(
            [-5, -4, -3, 3, 4, 5]
        )

        payment_day = max(
            1,
            min(
                last_day,
                payment_day + shift
            )
        )

    payment_date = date(
        year,
        month_number,
        payment_day
    )

    # Never create a salary payment before
    # the customer joined the bank.

    if payment_date < customer_since:

        return None

    return payment_date


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC SALARY PAYMENT DATA GENERATOR")
    print("=" * 70)

    print(
        f"\nRandom seed: {RANDOM_SEED}"
    )

    months = generate_months()

    print(
        f"Generating salary history: "
        f"{len(months)} months"
    )

    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # LOAD CUSTOMERS
        # ----------------------------------------------------

        print("\nLoading customers...")

        cursor.execute("""
            SELECT
                customer_id,
                first_name,
                last_name,
                employment_status,
                monthly_income,
                customer_since
            FROM customers
        """)

        customers = cursor.fetchall()

        print(
            f"Loaded {len(customers):,} customers."
        )

        # ----------------------------------------------------
        # LOAD ACCOUNTS
        # ----------------------------------------------------

        print("\nLoading accounts...")

        cursor.execute("""
            SELECT
                account_id,
                customer_id,
                account_number,
                status,
                currency,
                open_date
            FROM accounts
            WHERE currency = 'ZMW'
              AND status IN ('Active', 'Dormant')
        """)

        accounts = cursor.fetchall()

        print(
            f"Loaded {len(accounts):,} eligible accounts."
        )

        # ----------------------------------------------------
        # MAP ACCOUNTS TO CUSTOMERS
        # ----------------------------------------------------

        customer_accounts = {}

        for account in accounts:

            customer_id = account[
                "customer_id"
            ]

            if customer_id not in customer_accounts:

                customer_accounts[
                    customer_id
                ] = []

            customer_accounts[
                customer_id
            ].append(account)

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("GENERATING SALARY PAYMENTS")
        print("=" * 70)

        payments = []

        existing_ids = set()

        customers_with_salary = 0
        customers_without_salary = 0

        missed_payments = 0

        for index, customer in enumerate(
            customers,
            start=1
        ):

            employment_status = (
                customer[
                    "employment_status"
                ]
                or ""
            )

            # ----------------------------------------------
            # Determine eligibility
            # ----------------------------------------------

            if employment_status == "Employed":

                eligible = (
                    random.random()
                    < EMPLOYED_PROBABILITY
                )

            elif employment_status == "Self-employed":

                eligible = (
                    random.random()
                    < SELF_EMPLOYED_PROBABILITY
                )

            else:

                eligible = False

            if not eligible:

                customers_without_salary += 1

                continue

            customer_id = customer[
                "customer_id"
            ]

            if customer_id not in customer_accounts:

                customers_without_salary += 1

                continue

            accounts_for_customer = (
                customer_accounts[
                    customer_id
                ]
            )

            # Prefer an active account
            active_accounts = [
                a
                for a in accounts_for_customer
                if a["status"] == "Active"
            ]

            if active_accounts:

                account = random.choice(
                    active_accounts
                )

            else:

                account = random.choice(
                    accounts_for_customer
                )

            employer = generate_employer()

            customer_salary_created = False

            for month in months:

                # ------------------------------------------
                # Don't create salary before bank relationship
                # ------------------------------------------

                payment_date = generate_payment_date(
                    month,
                    customer["customer_since"]
                )

                if payment_date is None:
                    continue

                # ------------------------------------------
                # Missing payment
                # ------------------------------------------

                if (
                    random.random()
                    < MISSED_PAYMENT_PROBABILITY
                ):

                    missed_payments += 1

                    continue

                # ------------------------------------------
                # Salary amount
                # ------------------------------------------

                amount = generate_salary_amount(
                    customer[
                        "monthly_income"
                    ],
                    employment_status
                )

                if amount is None:
                    continue

                # ------------------------------------------
                # Employer variation
                # ------------------------------------------

                payment_employer = employer

                if (
                    random.random()
                    < EMPLOYER_VARIATION_PROBABILITY
                ):

                    payment_employer = (
                        make_messy_employer_name(
                            employer
                        )
                    )

                # ------------------------------------------
                # Payment ID
                # ------------------------------------------

                salary_payment_id = (
                    generate_salary_payment_id(
                        existing_ids
                    )
                )

                payments.append(
                    (
                        salary_payment_id,
                        customer_id,
                        account["account_id"],
                        payment_employer,
                        payment_date,
                        amount,
                        month
                    )
                )

                customer_salary_created = True

            if customer_salary_created:

                customers_with_salary += 1

            else:

                customers_without_salary += 1

            # ----------------------------------------------
            # Progress
            # ----------------------------------------------

            if index % 1000 == 0:

                print(
                    f"  Processed "
                    f"{index:,} / "
                    f"{len(customers):,} customers"
                )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

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
            f"Customers with salary history: "
            f"{customers_with_salary:,}"
        )

        print(
            f"Customers without salary history: "
            f"{customers_without_salary:,}"
        )

        print(
            f"Salary payments generated: "
            f"{len(payments):,}"
        )

        print(
            f"Missed salary payments: "
            f"{missed_payments:,}"
        )

        if payments:

            total = sum(
                p[5]
                for p in payments
            )

            average = (
                total
                / Decimal(len(payments))
            )

            print(
                f"Total salary value: "
                f"K{total:,.2f}"
            )

            print(
                f"Average salary payment: "
                f"K{average:,.2f}"
            )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO salary_payments (
                salary_payment_id,
                customer_id,
                account_id,
                employer_name,
                payment_date,
                amount,
                salary_month
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """

        batch_size = 1000

        for start in range(
            0,
            len(payments),
            batch_size
        ):

            batch = payments[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            processed = min(
                start + batch_size,
                len(payments)
            )

            print(
                f"  {processed:,} / "
                f"{len(payments):,} "
                f"({processed / len(payments) * 100:6.2f}%)"
            )

        # ----------------------------------------------------
        # DATABASE VERIFICATION
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM salary_payments
        """)

        count = cursor.fetchone()["count"]

        print(
            f"\nSalary payments currently "
            f"in database: {count:,}"
        )

        cursor.execute("""
            SELECT
                sp.salary_payment_id,
                sp.customer_id,
                CONCAT(
                    c.first_name,
                    ' ',
                    c.last_name
                ) AS customer_name,
                sp.employer_name,
                sp.payment_date,
                sp.amount
            FROM salary_payments sp
            JOIN customers c
                ON sp.customer_id = c.customer_id
            ORDER BY RAND()
            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample salary payments:\n")

        for row in rows:

            print(
                f"{row['salary_payment_id']} | "
                f"{row['customer_id']} | "
                f"{row['customer_name']} | "
                f"{row['employer_name']} | "
                f"{row['payment_date']} | "
                f"K{row['amount']:,.2f}"
            )

        print(
            "\n✓ Salary payment table "
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
        "KWACHA BANK SALARY PAYMENT "
        "GENERATION FINISHED"
    )
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()