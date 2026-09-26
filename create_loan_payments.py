import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import random
import math


# ============================================================
# KWACHA BANK
# SYNTHETIC LOAN PAYMENT DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)


# ============================================================
# PAYMENT METHODS
# ============================================================

PAYMENT_METHODS = [
    "Bank Transfer",
    "Mobile Banking",
    "Direct Debit",
    "Branch Cash",
    "ATM",
    "Salary Deduction",
    "Standing Order"
]


PAYMENT_METHOD_WEIGHTS = [
    25,
    20,
    20,
    8,
    3,
    15,
    9
]


# ============================================================
# PAYMENT STATUSES
# ============================================================

# These are the possible outcomes for individual payments.
#
# Paid
# Late
# Partial
# Missed
# Overpaid
#
# The actual probabilities are influenced by the loan status
# and customer's credit score.
# ============================================================


# ============================================================
# DATABASE CONNECTION
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
# SAFE DATE FUNCTION
# ============================================================

def safe_date(year, month, day):

    """
    Prevents invalid dates such as February 30.
    """

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    last_day = (next_month - timedelta(days=1)).day

    day = min(day, last_day)

    return date(year, month, day)


# ============================================================
# ADD MONTHS
# ============================================================

def add_months(start_date, months):

    """
    Adds months while preserving a sensible day of month.
    """

    month_index = start_date.month - 1 + months

    year = start_date.year + month_index // 12

    month = month_index % 12 + 1

    return safe_date(
        year,
        month,
        start_date.day
    )


# ============================================================
# ROUND MONEY
# ============================================================

def money(value):

    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# GENERATE PAYMENT ID
# ============================================================

def generate_payment_id(sequence):

    """
    Payment IDs are intentionally not simply PAYMENT000001,
    PAYMENT000002, etc.

    We use a bank-style identifier with a random component.
    """

    random_part = ''.join(
        random.choices(
            "ABCDEFGHJKLMNPQRSTUVWXYZ23456789",
            k=7
        )
    )

    return f"PAY-{random_part}-{sequence:05d}"


# ============================================================
# CREDIT SCORE EFFECT
# ============================================================

def credit_score_risk(credit_score):

    if credit_score is None:
        return 0.20

    if credit_score >= 750:
        return 0.05

    elif credit_score >= 700:
        return 0.08

    elif credit_score >= 650:
        return 0.14

    elif credit_score >= 600:
        return 0.22

    elif credit_score >= 550:
        return 0.32

    else:
        return 0.45


# ============================================================
# LOAN STATUS RISK
# ============================================================

def loan_status_risk(status):

    status = (status or "").lower()

    if status == "completed":
        return 0.04

    elif status == "active":
        return 0.10

    elif status == "approved":
        return 0.08

    elif status == "overdue":
        return 0.38

    elif status == "defaulted":
        return 0.65

    elif status == "written off":
        return 0.80

    elif status == "rejected":
        return None

    return 0.15


# ============================================================
# DETERMINE PAYMENT STATUS
# ============================================================

def determine_payment_status(
    loan_status,
    credit_score
):

    risk = credit_score_risk(credit_score)

    status_risk = loan_status_risk(loan_status)

    if status_risk is None:
        return None

    # Combine customer risk and loan risk.
    combined_risk = min(
        0.90,
        (risk * 0.45) + (status_risk * 0.55)
    )

    roll = random.random()

    # Missed payment
    if roll < combined_risk * 0.20:

        return "Missed"

    # Partial payment
    elif roll < combined_risk * 0.35:

        return "Partial"

    # Late payment
    elif roll < combined_risk:

        return "Late"

    # Small chance of overpayment
    elif random.random() < 0.015:

        return "Overpaid"

    return "Paid"


# ============================================================
# CALCULATE MONTHLY INSTALLMENT
# ============================================================

def calculate_installment(
    principal,
    annual_rate,
    months
):

    """
    Standard amortizing loan formula.
    """

    principal = Decimal(str(principal))

    annual_rate = Decimal(str(annual_rate))

    months = int(months)

    if months <= 0:
        return principal

    monthly_rate = (
        annual_rate / Decimal("100")
    ) / Decimal("12")

    if monthly_rate == 0:

        return money(
            principal / Decimal(months)
        )

    numerator = (
        monthly_rate *
        (
            Decimal("1") +
            monthly_rate
        ) ** months
    )

    denominator = (
        (
            Decimal("1") +
            monthly_rate
        ) ** months
    ) - Decimal("1")

    installment = principal * (
        numerator / denominator
    )

    return money(installment)


# ============================================================
# GENERATE PAYMENT BREAKDOWN
# ============================================================

def payment_breakdown(
    amount_due,
    loan_amount,
    interest_rate,
    remaining_balance
):

    """
    Creates a realistic split between principal and interest.
    """

    amount_due = money(amount_due)

    loan_amount = Decimal(str(loan_amount))

    interest_rate = Decimal(str(interest_rate))

    remaining_balance = Decimal(
        str(remaining_balance)
    )

    monthly_interest = money(
        remaining_balance *
        (
            interest_rate /
            Decimal("100") /
            Decimal("12")
        )
    )

    interest_paid = min(
        amount_due,
        monthly_interest
    )

    principal_paid = money(
        amount_due - interest_paid
    )

    return (
        principal_paid,
        interest_paid
    )


# ============================================================
# GENERATE PAYMENT
# ============================================================

def generate_payment(
    loan,
    payment_number
):

    loan_id = loan["loan_id"]

    application_date = loan["application_date"]

    disbursement_date = loan["disbursement_date"]

    loan_amount = Decimal(
        str(loan["loan_amount"] or 0)
    )

    interest_rate = Decimal(
        str(loan["interest_rate"] or 0)
    )

    term_months = int(
        loan["term_months"] or 12
    )

    monthly_installment = (
        loan["monthly_installment"]
    )

    outstanding_balance = Decimal(
        str(
            loan["outstanding_balance"]
            or 0
        )
    )

    loan_status = loan["loan_status"]

    credit_score = loan["credit_score"]

    if disbursement_date is None:

        if application_date is None:
            return None

        disbursement_date = application_date + timedelta(
            days=random.randint(2, 20)
        )

    # Payment number determines payment month.
    payment_date = add_months(
        disbursement_date,
        payment_number
    )

    # Add some realistic date variation.
    payment_date += timedelta(
        days=random.randint(-4, 8)
    )

    # Do not generate payments before disbursement.
    if payment_date <= disbursement_date:

        payment_date = disbursement_date + timedelta(
            days=random.randint(20, 35)
        )

    payment_status = determine_payment_status(
        loan_status,
        credit_score
    )

    if payment_status is None:
        return None

    # --------------------------------------------------------
    # Determine amount due
    # --------------------------------------------------------

    if monthly_installment:

        amount_due = Decimal(
            str(monthly_installment)
        )

    else:

        amount_due = calculate_installment(
            loan_amount,
            interest_rate,
            term_months
        )

    amount_due = money(amount_due)

    # --------------------------------------------------------
    # Determine amount paid
    # --------------------------------------------------------

    if payment_status == "Paid":

        amount_paid = amount_due

        # Occasionally pay a few kwacha extra.
        if random.random() < 0.02:

            amount_paid = money(
                amount_due +
                Decimal(
                    str(
                        random.uniform(
                            1,
                            100
                        )
                    )
                )
            )

    elif payment_status == "Late":

        amount_paid = amount_due

    elif payment_status == "Partial":

        percentage = Decimal(
            str(
                random.uniform(
                    0.25,
                    0.85
                )
            )
        )

        amount_paid = money(
            amount_due * percentage
        )

    elif payment_status == "Missed":

        amount_paid = Decimal("0.00")

    elif payment_status == "Overpaid":

        amount_paid = money(
            amount_due *
            Decimal(
                str(
                    random.uniform(
                        1.02,
                        1.15
                    )
                )
            )
        )

    else:

        amount_paid = amount_due

    # --------------------------------------------------------
    # Days late
    # --------------------------------------------------------

    if payment_status == "Late":

        days_late = random.randint(
            1,
            60
        )

        # Some severe late payments
        if random.random() < 0.08:

            days_late = random.randint(
                61,
                120
            )

    elif payment_status == "Partial":

        days_late = random.randint(
            0,
            45
        )

    elif payment_status == "Missed":

        days_late = random.randint(
            15,
            120
        )

    else:

        days_late = random.choice(
            [0, 0, 0, 0, 1, 2]
        )

    # --------------------------------------------------------
    # Principal / interest
    # --------------------------------------------------------

    principal_paid, interest_paid = (
        payment_breakdown(
            amount_paid,
            loan_amount,
            interest_rate,
            outstanding_balance
        )
    )

    # Never allow principal paid to be negative.
    principal_paid = max(
        Decimal("0.00"),
        principal_paid
    )

    interest_paid = max(
        Decimal("0.00"),
        interest_paid
    )

    # --------------------------------------------------------
    # Payment method
    # --------------------------------------------------------

    payment_method = random.choices(
        PAYMENT_METHODS,
        weights=PAYMENT_METHOD_WEIGHTS,
        k=1
    )[0]

    return {

        "loan_id": loan_id,

        "payment_date": payment_date,

        "amount_due": amount_due,

        "amount_paid": amount_paid,

        "principal_paid": principal_paid,

        "interest_paid": interest_paid,

        "days_late": days_late,

        "payment_status": payment_status,

        "payment_method": payment_method
    }


# ============================================================
# DETERMINE NUMBER OF PAYMENTS
# ============================================================

def determine_payment_count(loan):

    status = (
        loan["loan_status"]
        or ""
    ).lower()

    term = int(
        loan["term_months"]
        or 12
    )

    # Rejected loans have no payments.
    if status == "rejected":

        return 0

    # --------------------------------------------------------
    # Completed loans
    # --------------------------------------------------------

    if status == "completed":

        # Most completed loans have almost the full term.
        minimum = max(
            2,
            int(term * 0.70)
        )

        return random.randint(
            minimum,
            term
        )

    # --------------------------------------------------------
    # Active loans
    # --------------------------------------------------------

    if status == "active":

        return random.randint(
            2,
            max(
                3,
                min(
                    term,
                    30
                )
            )
        )

    # --------------------------------------------------------
    # Overdue
    # --------------------------------------------------------

    if status == "overdue":

        return random.randint(
            3,
            max(
                4,
                min(
                    term,
                    24
                )
            )
        )

    # --------------------------------------------------------
    # Defaulted
    # --------------------------------------------------------

    if status == "defaulted":

        return random.randint(
            2,
            max(
                3,
                min(
                    term,
                    18
                )
            )
        )

    # --------------------------------------------------------
    # Written off
    # --------------------------------------------------------

    if status == "written off":

        return random.randint(
            1,
            max(
                2,
                min(
                    term,
                    15
                )
            )
        )

    # Approved loans may have no payment yet,
    # but occasionally have one.
    if status == "approved":

        if random.random() < 0.15:

            return 1

        return 0

    return random.randint(
        1,
        min(term, 12)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC LOAN PAYMENT DATA GENERATOR")
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

    payments = []

    try:

        # ----------------------------------------------------
        # LOAD LOANS
        # ----------------------------------------------------

        print("\nLoading loans...")

        cursor.execute("""
            SELECT
                loan_id,
                customer_id,
                application_date,
                approval_date,
                disbursement_date,
                loan_amount,
                interest_rate,
                term_months,
                monthly_installment,
                outstanding_balance,
                loan_status,
                credit_score
            FROM loans
            ORDER BY loan_id
        """)

        loans = cursor.fetchall()

        print(
            f"Loaded {len(loans):,} loans."
        )

        # ----------------------------------------------------
        # GENERATE PAYMENTS
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("GENERATING LOAN PAYMENTS")
        print("=" * 70)

        payment_sequence = 1

        loan_payment_counts = {}

        for index, loan in enumerate(loans, start=1):

            count = determine_payment_count(
                loan
            )

            loan_payment_counts[
                loan["loan_id"]
            ] = count

            for payment_number in range(
                count
            ):

                payment = generate_payment(
                    loan,
                    payment_number
                )

                if payment is not None:

                    payment[
                        "payment_id"
                    ] = generate_payment_id(
                        payment_sequence
                    )

                    payments.append(
                        payment
                    )

                    payment_sequence += 1

            if index % 500 == 0:

                print(
                    f"  Processed "
                    f"{index:,} / "
                    f"{len(loans):,} loans"
                )

        print("\nGeneration completed.")

        # ====================================================
        # VALIDATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        print(
            f"\nPayments generated: "
            f"{len(payments):,}"
        )

        # ----------------------------------------------------
        # Payment status
        # ----------------------------------------------------

        status_counts = {}

        for payment in payments:

            status = payment[
                "payment_status"
            ]

            status_counts[status] = (
                status_counts.get(
                    status,
                    0
                ) + 1
            )

        print("\nPayment status:")

        for status, count in sorted(
            status_counts.items(),
            key=lambda x: -x[1]
        ):

            percentage = (
                count /
                len(payments)
            ) * 100

            print(
                f"  {status:<12} "
                f"{count:>7,} "
                f"({percentage:5.2f}%)"
            )

        # ----------------------------------------------------
        # Payment methods
        # ----------------------------------------------------

        method_counts = {}

        for payment in payments:

            method = payment[
                "payment_method"
            ]

            method_counts[method] = (
                method_counts.get(
                    method,
                    0
                ) + 1
            )

        print("\nPayment methods:")

        for method, count in sorted(
            method_counts.items(),
            key=lambda x: -x[1]
        ):

            print(
                f"  {method:<20} "
                f"{count:>7,}"
            )

        # ----------------------------------------------------
        # Total amount
        # ----------------------------------------------------

        total_due = sum(
            (
                p["amount_due"]
                for p in payments
            ),
            Decimal("0")
        )

        total_paid = sum(
            (
                p["amount_paid"]
                for p in payments
            ),
            Decimal("0")
        )

        total_principal = sum(
            (
                p["principal_paid"]
                for p in payments
            ),
            Decimal("0")
        )

        total_interest = sum(
            (
                p["interest_paid"]
                for p in payments
            ),
            Decimal("0")
        )

        print(
            f"\nTotal amount due: "
            f"K{total_due:,.2f}"
        )

        print(
            f"Total amount paid: "
            f"K{total_paid:,.2f}"
        )

        print(
            f"Total principal paid: "
            f"K{total_principal:,.2f}"
        )

        print(
            f"Total interest paid: "
            f"K{total_interest:,.2f}"
        )

        # ----------------------------------------------------
        # Late payments
        # ----------------------------------------------------

        late_payments = sum(
            1
            for p in payments
            if p["days_late"] > 0
        )

        print(
            f"\nPayments with late days: "
            f"{late_payments:,}"
        )

        # ====================================================
        # INSERT
        # ====================================================

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO loan_payments (
                payment_id,
                loan_id,
                payment_date,
                amount_due,
                amount_paid,
                principal_paid,
                interest_paid,
                days_late,
                payment_status,
                payment_method
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        batch_size = 1000

        inserted = 0

        for start in range(
            0,
            len(payments),
            batch_size
        ):

            batch = payments[
                start:start + batch_size
            ]

            data = []

            for p in batch:

                data.append(
                    (
                        p["payment_id"],
                        p["loan_id"],
                        p["payment_date"],
                        p["amount_due"],
                        p["amount_paid"],
                        p["principal_paid"],
                        p["interest_paid"],
                        p["days_late"],
                        p["payment_status"],
                        p["payment_method"]
                    )
                )

            cursor.executemany(
                insert_sql,
                data
            )

            inserted += len(data)

            connection.commit()

            print(
                f"  {inserted:,} / "
                f"{len(payments):,} "
                f"("
                f"{inserted / len(payments) * 100:6.2f}%"
                f")"
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
            FROM loan_payments
        """)

        database_count = cursor.fetchone()[
            "COUNT(*)"
        ]

        print(
            f"\nLoan payments currently in database: "
            f"{database_count:,}"
        )

        # ----------------------------------------------------
        # Sample
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                lp.payment_id,
                lp.loan_id,
                c.first_name,
                c.last_name,
                lp.payment_date,
                lp.amount_due,
                lp.amount_paid,
                lp.days_late,
                lp.payment_status,
                lp.payment_method
            FROM loan_payments lp
            JOIN loans l
                ON lp.loan_id = l.loan_id
            JOIN customers c
                ON l.customer_id = c.customer_id
            ORDER BY RAND()
            LIMIT 10
        """)

        samples = cursor.fetchall()

        print("\nSample payments:\n")

        for row in samples:

            print(
                f"{row['payment_id']} | "
                f"{row['loan_id']} | "
                f"{row['first_name']} "
                f"{row['last_name']} | "
                f"{row['payment_date']} | "
                f"Due K{row['amount_due']:,.2f} | "
                f"Paid K{row['amount_paid']:,.2f} | "
                f"{row['days_late']} days late | "
                f"{row['payment_status']} | "
                f"{row['payment_method']}"
            )

        print(
            "\n✓ Loan payment table successfully populated."
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
        "KWACHA BANK LOAN PAYMENT GENERATION FINISHED"
    )
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()