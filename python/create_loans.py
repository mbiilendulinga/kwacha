import mysql.connector
from mysql.connector import Error
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
import random
import string
import math


# ============================================================
# KWACHA BANK
# SYNTHETIC LOAN DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_LOANS = 5000

# Historical period
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)

# Probability that an eligible customer has a loan
BASE_LOAN_PROBABILITY = 0.32


# ============================================================
# LOAN PRODUCT PREFERENCES
# ============================================================

PRODUCT_WEIGHTS = {

    "Personal": 0.23,

    "Salary Advance": 0.14,

    "Education": 0.05,

    "Asset Finance": 0.10,

    "Mortgage": 0.05,

    "Business": 0.18,

    "Agriculture": 0.08,

    "Microfinance": 0.10,

    "Credit Facility": 0.04,

    "Premium": 0.03
}


# ============================================================
# RANDOM ID GENERATORS
# ============================================================

def generate_random_id(prefix, existing_ids, length=10):

    characters = string.ascii_uppercase + string.digits

    while True:

        random_part = "".join(
            random.choices(
                characters,
                k=length
            )
        )

        value = f"{prefix}-{random_part}"

        if value not in existing_ids:

            existing_ids.add(value)

            return value


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
# DATE HELPERS
# ============================================================

def random_date(start_date, end_date):

    if start_date > end_date:

        return start_date

    days = (
        end_date - start_date
    ).days

    return (
        start_date
        + timedelta(
            days=random.randint(
                0,
                days
            )
        )
    )


# ============================================================
# WEIGHTED PRODUCT SELECTION
# ============================================================

def choose_product(products):

    categories = list(
        PRODUCT_WEIGHTS.keys()
    )

    weights = list(
        PRODUCT_WEIGHTS.values()
    )

    category = random.choices(
        categories,
        weights=weights,
        k=1
    )[0]

    candidates = [
        p
        for p in products
        if p["loan_category"] == category
    ]

    # Fallback if category does not exist
    if not candidates:

        return random.choice(products)

    return random.choice(candidates)


# ============================================================
# CUSTOMER LOAN ELIGIBILITY
# ============================================================

def calculate_loan_probability(customer):

    probability = BASE_LOAN_PROBABILITY

    employment = (
        customer["employment_status"]
        or ""
    )

    segment = (
        customer["customer_segment"]
        or ""
    )

    risk = (
        customer["risk_rating"]
        or ""
    )

    income = (
        Decimal(str(customer["monthly_income"]))
        if customer["monthly_income"] is not None
        else Decimal("0")
    )

    age = customer["age"]

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    if employment == "Employed":

        probability += 0.20

    elif employment == "Self-employed":

        probability += 0.15

    elif employment == "Retired":

        probability -= 0.05

    elif employment == "Student":

        probability -= 0.15

    elif employment == "Unemployed":

        probability -= 0.20

    # --------------------------------------------------------
    # Income
    # --------------------------------------------------------

    if income >= 30000:

        probability += 0.15

    elif income >= 15000:

        probability += 0.10

    elif income >= 8000:

        probability += 0.05

    elif income < 2000:

        probability -= 0.10

    # --------------------------------------------------------
    # Customer segment
    # --------------------------------------------------------

    if segment == "Business":

        probability += 0.12

    elif segment == "Mass Affluent":

        probability += 0.10

    elif segment == "Affluent":

        probability += 0.12

    elif segment == "Youth":

        probability -= 0.03

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    if risk == "Low":

        probability += 0.08

    elif risk == "High":

        probability -= 0.15

    # --------------------------------------------------------
    # Age
    # --------------------------------------------------------

    if age < 21:

        probability -= 0.20

    elif age >= 25 and age <= 55:

        probability += 0.05

    elif age > 65:

        probability -= 0.08

    return max(
        0.02,
        min(
            0.90,
            probability
        )
    )


# ============================================================
# CREDIT SCORE
# ============================================================

def generate_credit_score(customer):

    risk = customer["risk_rating"]

    income = (
        Decimal(str(customer["monthly_income"]))
        if customer["monthly_income"] is not None
        else Decimal("0")
    )

    employment = (
        customer["employment_status"]
        or ""
    )

    score = 550

    # Risk rating
    if risk == "Low":

        score += random.randint(
            80,
            170
        )

    elif risk == "Medium":

        score += random.randint(
            20,
            90
        )

    elif risk == "High":

        score -= random.randint(
            20,
            100
        )

    # Income
    if income >= 30000:

        score += random.randint(
            20,
            70
        )

    elif income >= 15000:

        score += random.randint(
            10,
            45
        )

    elif income < 3000:

        score -= random.randint(
            10,
            50
        )

    # Employment
    if employment == "Employed":

        score += random.randint(
            10,
            35
        )

    elif employment == "Self-employed":

        score += random.randint(
            0,
            25
        )

    elif employment == "Unemployed":

        score -= random.randint(
            20,
            60
        )

    # Random noise
    score += random.randint(
        -25,
        25
    )

    return max(
        300,
        min(
            850,
            score
        )
    )


# ============================================================
# DEFAULT PROBABILITY
# ============================================================

def calculate_default_probability(
    customer,
    credit_score
):

    probability = 0.12

    risk = customer["risk_rating"]

    employment = (
        customer["employment_status"]
        or ""
    )

    income = (
        Decimal(str(customer["monthly_income"]))
        if customer["monthly_income"] is not None
        else Decimal("0")
    )

    # Risk
    if risk == "Low":

        probability -= 0.06

    elif risk == "High":

        probability += 0.18

    # Credit score
    if credit_score >= 750:

        probability -= 0.07

    elif credit_score >= 650:

        probability -= 0.03

    elif credit_score < 550:

        probability += 0.10

    # Employment
    if employment == "Unemployed":

        probability += 0.15

    elif employment == "Self-employed":

        probability += 0.04

    elif employment == "Employed":

        probability -= 0.03

    # Income
    if income >= 30000:

        probability -= 0.04

    elif income < 5000:

        probability += 0.08

    # Random noise
    probability += random.uniform(
        -0.025,
        0.025
    )

    return max(
        0.01,
        min(
            0.85,
            probability
        )
    )


# ============================================================
# LOAN AMOUNT
# ============================================================

def generate_loan_amount(
    customer,
    product
):

    minimum = Decimal(
        str(product["minimum_amount"])
    )

    maximum = Decimal(
        str(product["maximum_amount"])
    )

    income = (
        Decimal(str(customer["monthly_income"]))
        if customer["monthly_income"] is not None
        else Decimal("0")
    )

    segment = customer["customer_segment"]

    # --------------------------------------------------------
    # Income-based affordability
    # --------------------------------------------------------

    if income <= 0:

        affordability = minimum

    else:

        affordability = income * Decimal(
            str(
                random.uniform(
                    2.0,
                    12.0
                )
            )
        )

    # --------------------------------------------------------
    # Segment adjustments
    # --------------------------------------------------------

    if segment == "Youth":

        affordability *= Decimal("0.55")

    elif segment == "Mass Affluent":

        affordability *= Decimal("1.35")

    elif segment == "Affluent":

        affordability *= Decimal("1.80")

    elif segment == "Business":

        affordability *= Decimal("1.50")

    # --------------------------------------------------------
    # Keep inside product limits
    # --------------------------------------------------------

    upper = min(
        maximum,
        max(
            minimum,
            affordability
        )
    )

    if upper <= minimum:

        amount = minimum

    else:

        # Weighted toward smaller loans
        fraction = random.random() ** 1.7

        amount = (
            minimum
            + (
                upper - minimum
            ) * Decimal(str(fraction))
        )

    # Round to nearest K100
    amount = (
        amount / Decimal("100")
    ).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    ) * Decimal("100")

    return max(
        minimum,
        min(
            maximum,
            amount
        )
    )


# ============================================================
# INTEREST RATE
# ============================================================

def generate_interest_rate(product):

    base = Decimal(
        str(product["base_interest_rate"])
    )

    variation = Decimal(
        str(
            random.uniform(
                -2.0,
                3.0
            )
        )
    )

    rate = base + variation

    return max(
        Decimal("5.00"),
        rate
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# LOAN TERM
# ============================================================

def generate_term(product):

    maximum = product[
        "maximum_term_months"
    ]

    if maximum <= 12:

        options = [
            x
            for x in [
                3,
                6,
                9,
                12
            ]
            if x <= maximum
        ]

    elif maximum <= 36:

        options = [
            x
            for x in [
                6,
                12,
                18,
                24,
                36
            ]
            if x <= maximum
        ]

    elif maximum <= 72:

        options = [
            x
            for x in [
                12,
                24,
                36,
                48,
                60,
                72
            ]
            if x <= maximum
        ]

    else:

        options = [
            x
            for x in [
                60,
                84,
                120,
                180,
                240
            ]
            if x <= maximum
        ]

    return random.choice(options)


# ============================================================
# MONTHLY INSTALLMENT
# ============================================================

def calculate_monthly_installment(
    principal,
    annual_rate,
    term_months
):

    monthly_rate = (
        annual_rate
        / Decimal("100")
        / Decimal("12")
    )

    if monthly_rate == 0:

        payment = (
            principal
            / Decimal(term_months)
        )

    else:

        factor = (
            Decimal("1")
            + monthly_rate
        ) ** term_months

        payment = (
            principal
            * monthly_rate
            * factor
            / (
                factor
                - Decimal("1")
            )
        )

    return payment.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# COLLATERAL VALUE
# ============================================================

def generate_collateral_value(
    product,
    loan_amount
):

    if not product["collateral_required"]:

        # Some unsecured loans still have
        # recorded collateral information.
        if random.random() < 0.05:

            return (
                loan_amount
                * Decimal(
                    str(
                        random.uniform(
                            1.0,
                            1.5
                        )
                    )
                )
            ).quantize(
                Decimal("0.01")
            )

        return None

    # Secured lending normally has collateral
    multiplier = random.uniform(
        1.05,
        1.70
    )

    value = (
        loan_amount
        * Decimal(str(multiplier))
    )

    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# LOAN STATUS
# ============================================================

def determine_loan_status(
    application_date,
    approval_date,
    disbursement_date,
    default_probability
):

    # Rejected applications
    if approval_date is None:

        return "Rejected"

    # Approved but not disbursed
    if disbursement_date is None:

        return "Approved"

    # Default probability influences outcome
    random_value = random.random()

    if random_value < default_probability * 0.35:

        return "Defaulted"

    if random_value < default_probability * 0.80:

        return "Overdue"

    if random.random() < 0.04:

        return "Written Off"

    # Some loans have been fully repaid
    if random.random() < 0.30:

        return "Completed"

    return "Active"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC LOAN DATA GENERATOR")
    print("=" * 70)

    print(
        f"\nTarget loans: {TARGET_LOANS:,}"
    )

    print(
        f"Random seed: {RANDOM_SEED}"
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
                date_of_birth,
                employment_status,
                monthly_income,
                customer_since,
                risk_rating,
                customer_segment
            FROM customers
        """)

        customers = cursor.fetchall()

        print(
            f"Loaded {len(customers):,} customers."
        )

        # Add age
        today = date(
            2025,
            12,
            31
        )

        for customer in customers:

            dob = customer[
                "date_of_birth"
            ]

            age = (
                today.year
                - dob.year
                - (
                    (
                        today.month,
                        today.day
                    )
                    <
                    (
                        dob.month,
                        dob.day
                    )
                )
            )

            customer["age"] = age

        # ----------------------------------------------------
        # LOAD LOAN PRODUCTS
        # ----------------------------------------------------

        print("\nLoading loan products...")

        cursor.execute("""
            SELECT
                loan_product_id,
                product_name,
                loan_category,
                minimum_amount,
                maximum_amount,
                base_interest_rate,
                maximum_term_months,
                collateral_required
            FROM loan_products
        """)

        products = cursor.fetchall()

        print(
            f"Loaded {len(products):,} loan products."
        )

        # ----------------------------------------------------
        # LOAD BRANCHES
        # ----------------------------------------------------

        print("\nLoading branches...")

        cursor.execute("""
            SELECT
                branch_id
            FROM branches
        """)

        branches = cursor.fetchall()

        print(
            f"Loaded {len(branches):,} branches."
        )

        # ----------------------------------------------------
        # LOAD SALARY INFORMATION
        # ----------------------------------------------------

        print("\nLoading salary payment history...")

        cursor.execute("""
            SELECT
                customer_id,
                COUNT(*) AS salary_count,
                AVG(amount) AS average_salary
            FROM salary_payments
            GROUP BY customer_id
        """)

        salary_data = cursor.fetchall()

        salary_map = {
            row["customer_id"]: row
            for row in salary_data
        }

        print(
            f"Loaded salary information "
            f"for {len(salary_map):,} customers."
        )

        # ----------------------------------------------------
        # GENERATE LOANS
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("GENERATING LOANS")
        print("=" * 70)

        loans = []

        existing_ids = set()

        attempts = 0

        max_attempts = TARGET_LOANS * 20

        while (
            len(loans) < TARGET_LOANS
            and attempts < max_attempts
        ):

            attempts += 1

            customer = random.choice(
                customers
            )

            probability = (
                calculate_loan_probability(
                    customer
                )
            )

            # Customers with salary history
            # become more likely to obtain loans.
            if customer["customer_id"] in salary_map:

                probability += 0.07

            probability = min(
                probability,
                0.95
            )

            if random.random() > probability:

                continue

            # ------------------------------------------------
            # Product
            # ------------------------------------------------

            product = choose_product(
                products
            )

            # ------------------------------------------------
            # Product/customer compatibility
            # ------------------------------------------------

            employment = (
                customer["employment_status"]
                or ""
            )

            segment = (
                customer["customer_segment"]
                or ""
            )

            # Business products
            if product["loan_category"] == "Business":

                if (
                    employment != "Self-employed"
                    and segment != "Business"
                ):

                    if random.random() < 0.75:

                        continue

            # Agriculture
            if product["loan_category"] == "Agriculture":

                if random.random() < 0.35:

                    continue

            # Mortgage
            if product["loan_category"] == "Mortgage":

                if customer["age"] < 25:

                    continue

            # Education
            if product["loan_category"] == "Education":

                if (
                    customer["age"] > 50
                    and random.random() < 0.70
                ):

                    continue

            # ------------------------------------------------
            # Application date
            # ------------------------------------------------

            customer_since = customer[
                "customer_since"
            ]

            earliest_date = max(
                START_DATE,
                customer_since
            )

            if earliest_date > END_DATE:

                continue

            application_date = random_date(
                earliest_date,
                END_DATE
            )

            # ------------------------------------------------
            # Approval decision
            # ------------------------------------------------

            credit_score = (
                generate_credit_score(
                    customer
                )
            )

            approval_probability = 0.78

            if credit_score >= 750:

                approval_probability += 0.12

            elif credit_score >= 650:

                approval_probability += 0.05

            elif credit_score < 550:

                approval_probability -= 0.20

            if customer["risk_rating"] == "High":

                approval_probability -= 0.20

            elif customer["risk_rating"] == "Low":

                approval_probability += 0.08

            approval_probability = max(
                0.05,
                min(
                    0.98,
                    approval_probability
                )
            )

            approved = (
                random.random()
                < approval_probability
            )

            if approved:

                approval_delay = random.randint(
                    1,
                    14
                )

                approval_date = (
                    application_date
                    + timedelta(
                        days=approval_delay
                    )
                )

                if approval_date > END_DATE:

                    approval_date = END_DATE

                # ------------------------------------------------
                # Disbursement
                # ------------------------------------------------

                if random.random() < 0.94:

                    disbursement_delay = random.randint(
                        1,
                        7
                    )

                    disbursement_date = (
                        approval_date
                        + timedelta(
                            days=disbursement_delay
                        )
                    )

                    if (
                        disbursement_date
                        > END_DATE
                    ):

                        disbursement_date = END_DATE

                else:

                    disbursement_date = None

            else:

                approval_date = None

                disbursement_date = None

            # ------------------------------------------------
            # Loan amount
            # ------------------------------------------------

            loan_amount = generate_loan_amount(
                customer,
                product
            )

            interest_rate = (
                generate_interest_rate(
                    product
                )
            )

            term_months = generate_term(
                product
            )

            monthly_installment = (
                calculate_monthly_installment(
                    loan_amount,
                    interest_rate,
                    term_months
                )
            )

            # ------------------------------------------------
            # Default probability
            # ------------------------------------------------

            default_probability = (
                calculate_default_probability(
                    customer,
                    credit_score
                )
            )

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            loan_status = (
                determine_loan_status(
                    application_date,
                    approval_date,
                    disbursement_date,
                    default_probability
                )
            )

            # ------------------------------------------------
            # Outstanding balance
            # ------------------------------------------------

            if loan_status == "Rejected":

                outstanding_balance = Decimal("0.00")

            elif loan_status == "Completed":

                outstanding_balance = Decimal("0.00")

            else:

                # Approximate remaining balance
                repayment_progress = random.uniform(
                    0.05,
                    0.90
                )

                outstanding_balance = (
                    loan_amount
                    * Decimal(
                        str(
                            1
                            - repayment_progress
                        )
                    )
                )

                if loan_status == "Defaulted":

                    outstanding_balance *= Decimal(
                        str(
                            random.uniform(
                                0.30,
                                0.85
                            )
                        )
                    )

                elif loan_status == "Written Off":

                    outstanding_balance *= Decimal(
                        str(
                            random.uniform(
                                0.05,
                                0.30
                            )
                        )
                    )

                outstanding_balance = (
                    outstanding_balance
                    .quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP
                    )
                )

            # ------------------------------------------------
            # Collateral
            # ------------------------------------------------

            collateral_value = (
                generate_collateral_value(
                    product,
                    loan_amount
                )
            )

            # ------------------------------------------------
            # Branch
            # ------------------------------------------------

            branch = random.choice(
                branches
            )

            # ------------------------------------------------
            # ID
            # ------------------------------------------------

            loan_id = generate_random_id(
                "LN",
                existing_ids,
                10
            )

            # ------------------------------------------------
            # Append
            # ------------------------------------------------

            loans.append(
                (
                    loan_id,
                    customer["customer_id"],
                    product["loan_product_id"],
                    branch["branch_id"],
                    application_date,
                    approval_date,
                    disbursement_date,
                    loan_amount,
                    interest_rate,
                    term_months,
                    monthly_installment,
                    outstanding_balance,
                    loan_status,
                    credit_score,
                    collateral_value,
                    Decimal(
                        str(
                            round(
                                default_probability,
                                4
                            )
                        )
                    )
                )
            )

            if len(loans) % 500 == 0:

                print(
                    f"  Generated "
                    f"{len(loans):,} / "
                    f"{TARGET_LOANS:,} loans"
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
            f"\nLoans generated: "
            f"{len(loans):,}"
        )

        # Status
        status_counts = {}

        for loan in loans:

            status = loan[12]

            status_counts[
                status
            ] = status_counts.get(
                status,
                0
            ) + 1

        print("\nLoan status:")

        for status, count in sorted(
            status_counts.items()
        ):

            print(
                f"  {status:<15} "
                f"{count:,}"
            )

        # Product
        product_counts = {}

        for loan in loans:

            product_id = loan[2]

            product_counts[
                product_id
            ] = product_counts.get(
                product_id,
                0
            ) + 1

        print("\nLoan products:")

        for product_id, count in sorted(
            product_counts.items()
        ):

            print(
                f"  {product_id:<10} "
                f"{count:,}"
            )

        # Total value
        total_loan_value = sum(
            loan[7]
            for loan in loans
        )

        total_outstanding = sum(
            loan[11]
            for loan in loans
        )

        print(
            f"\nTotal loan value: "
            f"K{total_loan_value:,.2f}"
        )

        print(
            f"Total outstanding balance: "
            f"K{total_outstanding:,.2f}"
        )

        print(
            f"Average loan amount: "
            f"K{(
                total_loan_value
                / Decimal(len(loans))
            ):,.2f}"
        )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO loans (
                loan_id,
                customer_id,
                loan_product_id,
                branch_id,
                application_date,
                approval_date,
                disbursement_date,
                loan_amount,
                interest_rate,
                term_months,
                monthly_installment,
                outstanding_balance,
                loan_status,
                credit_score,
                collateral_value,
                default_probability
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        batch_size = 500

        for start in range(
            0,
            len(loans),
            batch_size
        ):

            batch = loans[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            processed = min(
                start + batch_size,
                len(loans)
            )

            print(
                f"  {processed:,} / "
                f"{len(loans):,} "
                f"({processed / len(loans) * 100:6.2f}%)"
            )

        # ----------------------------------------------------
        # VERIFICATION
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM loans
        """)

        count = cursor.fetchone()["count"]

        print(
            f"\nLoans currently in database: "
            f"{count:,}"
        )

        cursor.execute("""
            SELECT
                l.loan_id,
                l.customer_id,
                CONCAT(
                    c.first_name,
                    ' ',
                    c.last_name
                ) AS customer_name,
                lp.product_name,
                l.loan_amount,
                l.interest_rate,
                l.term_months,
                l.loan_status,
                l.credit_score
            FROM loans l
            JOIN customers c
                ON l.customer_id = c.customer_id
            JOIN loan_products lp
                ON l.loan_product_id =
                   lp.loan_product_id
            ORDER BY RAND()
            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample loans:\n")

        for row in rows:

            print(
                f"{row['loan_id']} | "
                f"{row['customer_id']} | "
                f"{row['customer_name']} | "
                f"{row['product_name']} | "
                f"K{row['loan_amount']:,.2f} | "
                f"{row['interest_rate']:.2f}% | "
                f"{row['term_months']} months | "
                f"{row['loan_status']} | "
                f"Score: {row['credit_score']}"
            )

        print(
            "\n✓ Loans table successfully populated."
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
        "KWACHA BANK LOAN GENERATION FINISHED"
    )
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()