import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
from decimal import Decimal
import random
from collections import Counter

# ============================================================
# KWACHA BANK
# SYNTHETIC EMPLOYEE DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)

# ============================================================
# ZAMBIAN NAMES
# ============================================================

MALE_FIRST_NAMES = [
    "Aaron", "Andrew", "Anthony", "Banda", "Blessings", "Brian",
    "Charles", "Chanda", "Christopher", "Collins", "Daniel",
    "David", "Douglas", "Edwin", "Elijah", "Emmanuel", "Evans",
    "Felix", "Francis", "Frederick", "George", "Gerald",
    "Gift", "Given", "Godfrey", "Isaac", "Jackson", "Jacob",
    "James", "Jason", "Joseph", "Joshua", "Justin", "Kennedy",
    "Kingsley", "Lawrence", "Leonard", "Lloyd", "Martin",
    "Mathews", "Michael", "Moses", "Mulenga", "Mwansa",
    "Nathan", "Nicholas", "Patrick", "Paul", "Peter",
    "Philemon", "Raphael", "Richard", "Robert", "Samuel",
    "Simon", "Stephen", "Sylvester", "Trevor", "Victor",
    "Vincent", "William"
]

FEMALE_FIRST_NAMES = [
    "Alice", "Agnes", "Beatrice", "Belinda", "Bertha", "Blessing",
    "Brenda", "Bridget", "Caroline", "Catherine", "Chanda",
    "Charity", "Chileshe", "Christine", "Claudia", "Diana",
    "Dorcas", "Edith", "Elizabeth", "Esther", "Faith",
    "Florence", "Frances", "Grace", "Hannah", "Helen",
    "Ireen", "Irene", "Jacqueline", "Jane", "Janet",
    "Jessica", "Josephine", "Joyce", "Judith", "Julia",
    "Karen", "Katherine", "Lillian", "Linda", "Loveness",
    "Lucy", "Margaret", "Maria", "Mary", "Mercy",
    "Monica", "Martha", "Miriam", "Natasha", "Patricia",
    "Pauline", "Rachel", "Rebecca", "Ruth", "Sandra",
    "Sharon", "Sheila", "Sophia", "Susan", "Theresa",
    "Valerie", "Veronica", "Winnie"
]

LAST_NAMES = [
    "Banda", "Chanda", "Chibesa", "Chilufya", "Chimuka",
    "Chisala", "Chishimba", "Chitembo", "Chituta", "Chomba",
    "Daka", "Funsani", "Hamukale", "Hamusonde", "Kabwe",
    "Kakoma", "Kalaba", "Kalonde", "Kalyalya", "Kamanga",
    "Kang'ombe", "Kapasa", "Katambo", "Katema", "Katembo",
    "Kayanda", "Kunda", "Lungu", "Manda", "Mbewe",
    "Mfula", "Michelo", "Milupi", "Minga", "Moyo",
    "Mubanga", "Mukuka", "Mulenga", "Mumba", "Musonda",
    "Mwale", "Mwansa", "Mwanza", "Mwelwa", "Nasilele",
    "Ng'andu", "Nkole", "Phiri", "Sakala", "Sampa",
    "Simukonda", "Sinkala", "Sitwala", "Tembo", "Wamunyima",
    "Zimba", "Zulu"
]

# ============================================================
# DEPARTMENTS AND JOBS
# ============================================================

JOB_STRUCTURE = {

    "Branch Operations": [
        ("Teller", 0.32, 6500, 11000),
        ("Senior Teller", 0.08, 9500, 15000),
        ("Operations Officer", 0.07, 11000, 18000),
        ("Branch Operations Manager", 0.025, 18000, 30000),
    ],

    "Customer Service": [
        ("Customer Service Officer", 0.12, 7000, 13000),
        ("Senior Customer Service Officer", 0.035, 10000, 17000),
        ("Customer Service Manager", 0.015, 17000, 28000),
    ],

    "Credit": [
        ("Credit Officer", 0.07, 9000, 17000),
        ("Senior Credit Officer", 0.025, 13000, 22000),
        ("Credit Manager", 0.012, 19000, 32000),
    ],

    "Loans": [
        ("Loan Officer", 0.055, 8500, 16000),
        ("Senior Loan Officer", 0.018, 12000, 20000),
        ("Loans Manager", 0.008, 19000, 32000),
    ],

    "Finance": [
        ("Finance Officer", 0.025, 10000, 19000),
        ("Senior Finance Officer", 0.012, 14000, 23000),
        ("Finance Manager", 0.006, 20000, 34000),
    ],

    "Human Resources": [
        ("HR Officer", 0.018, 9000, 17000),
        ("Senior HR Officer", 0.008, 13000, 22000),
        ("HR Manager", 0.004, 19000, 32000),
    ],

    "Information Technology": [
        ("IT Support Officer", 0.02, 9000, 17000),
        ("Systems Analyst", 0.015, 13000, 24000),
        ("Database Administrator", 0.008, 16000, 28000),
        ("IT Manager", 0.004, 22000, 38000),
    ],

    "Risk and Compliance": [
        ("Risk Officer", 0.018, 11000, 20000),
        ("Compliance Officer", 0.018, 11000, 20000),
        ("Senior Risk Officer", 0.008, 15000, 26000),
        ("Compliance Manager", 0.004, 20000, 34000),
    ],

    "Marketing": [
        ("Marketing Officer", 0.018, 8500, 16000),
        ("Digital Marketing Officer", 0.01, 9000, 18000),
        ("Marketing Manager", 0.004, 18000, 30000),
    ],
}

# ============================================================
# HELPERS
# ============================================================

def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, days))


def choose_gender():
    return random.choice(["Male", "Female"])


def generate_name():
    gender = choose_gender()

    if gender == "Male":
        first_name = random.choice(MALE_FIRST_NAMES)
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)

    last_name = random.choice(LAST_NAMES)

    return first_name, last_name


def generate_salary(min_salary, max_salary):
    """
    Generate salaries in a less-perfect way than simply
    choosing a random integer.

    Most salaries cluster toward the middle.
    """

    value = random.triangular(
        min_salary,
        max_salary,
        (min_salary + max_salary) / 2
    )

    return Decimal(str(round(value, 2)))


def generate_employment_date():
    """
    Most employees joined between 2016 and 2025.
    """

    start = date(2012, 1, 1)
    end = date(2026, 7, 31)

    return random_date(start, end)


def choose_job():
    """
    Flatten the job structure using weights.
    """

    choices = []

    for department, jobs in JOB_STRUCTURE.items():
        for job_title, weight, minimum, maximum in jobs:
            choices.append(
                (
                    department,
                    job_title,
                    weight,
                    minimum,
                    maximum
                )
            )

    total_weight = sum(x[2] for x in choices)

    r = random.random() * total_weight

    cumulative = 0

    for item in choices:
        cumulative += item[2]

        if r <= cumulative:
            return item[0], item[1], item[3], item[4]

    return choices[-1][0], choices[-1][1], choices[-1][3], choices[-1][4]


def generate_employee_status(employment_date):
    """
    Small proportion of employees are no longer active.
    """

    if random.random() < 0.91:
        return "Active"

    statuses = [
        "Resigned",
        "Retired",
        "Terminated",
        "On Leave"
    ]

    return random.choice(statuses)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC EMPLOYEE DATA GENERATOR")
    print("=" * 70)

    print()
    print(f"Random seed: {RANDOM_SEED}")
    print()

    connection = None
    cursor = None

    try:

        print("Connecting to MySQL...")

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # LOAD BRANCHES
        # ----------------------------------------------------

        print("Loading branches...")

        cursor.execute("""
            SELECT
                branch_id,
                branch_name,
                branch_type,
                city,
                province
            FROM branches
        """)

        branches = cursor.fetchall()

        print(f"Loaded {len(branches)} branches.")

        if not branches:
            raise Exception(
                "No branches found. Populate the branches table first."
            )

        # ----------------------------------------------------
        # GENERATE EMPLOYEES
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("GENERATING EMPLOYEES")
        print("=" * 70)

        employees = []

        employee_counter = 1

        # Branch staffing levels.
        #
        # Main / large branches receive more employees.
        # Smaller branches receive fewer.

        for branch in branches:

            branch_type = branch["branch_type"]

            if branch_type in ["Head Office", "Main Branch"]:
                employee_count = random.randint(35, 65)

            elif branch_type in ["Regional Branch", "Large Branch"]:
                employee_count = random.randint(20, 35)

            else:
                employee_count = random.randint(8, 20)

            for _ in range(employee_count):

                first_name, last_name = generate_name()

                department, job_title, min_salary, max_salary = choose_job()

                employment_date = generate_employment_date()

                salary = generate_salary(
                    min_salary,
                    max_salary
                )

                employment_status = generate_employee_status(
                    employment_date
                )

                employee_id = f"EMP{employee_counter:07d}"

                employees.append(
                    (
                        employee_id,
                        branch["branch_id"],
                        first_name,
                        last_name,
                        job_title,
                        department,
                        employment_date,
                        salary,
                        employment_status
                    )
                )

                employee_counter += 1

        print()
        print("Generation completed.")

        # ====================================================
        # VALIDATION
        # ====================================================

        print()
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        print()
        print(f"Employees generated: {len(employees):,}")

        department_counts = Counter(
            employee[5]
            for employee in employees
        )

        status_counts = Counter(
            employee[8]
            for employee in employees
        )

        print()
        print("Departments:")

        for department, count in department_counts.most_common():
            print(
                f"  {department:<25} {count:>5}"
            )

        print()
        print("Employment status:")

        for status, count in status_counts.most_common():
            print(
                f"  {status:<15} {count:>5}"
            )

        salaries = [
            employee[7]
            for employee in employees
        ]

        average_salary = sum(
            salaries,
            Decimal("0")
        ) / Decimal(len(salaries))

        print()
        print(
            f"Average salary: K{average_salary:,.2f}"
        )

        print()
        print("Sample employees:")

        for employee in employees[:10]:

            print(
                f"{employee[0]} | "
                f"{employee[2]} {employee[3]} | "
                f"{employee[5]} | "
                f"{employee[4]} | "
                f"{employee[1]} | "
                f"K{employee[7]:,.2f} | "
                f"{employee[8]}"
            )

        # ====================================================
        # INSERT
        # ====================================================

        print()
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO employees (
                employee_id,
                branch_id,
                first_name,
                last_name,
                job_title,
                department,
                employment_date,
                salary,
                employment_status
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        batch_size = 500

        for i in range(0, len(employees), batch_size):

            batch = employees[
                i:i + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            processed = min(
                i + batch_size,
                len(employees)
            )

            print(
                f"  {processed:,} / "
                f"{len(employees):,} "
                f"({processed / len(employees) * 100:6.2f}%)"
            )

        # ====================================================
        # DATABASE VERIFICATION
        # ====================================================

        print()
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM employees
        """)

        total = cursor.fetchone()["total"]

        print()
        print(
            f"Employees currently in database: {total:,}"
        )

        cursor.execute("""
            SELECT
                AVG(salary) AS avg_salary
            FROM employees
        """)

        result = cursor.fetchone()

        print(
            f"Average salary: K{result['avg_salary']:,.2f}"
        )

        cursor.execute("""
            SELECT
                employee_id,
                first_name,
                last_name,
                job_title,
                department,
                salary,
                employment_status
            FROM employees
            ORDER BY employee_id
            LIMIT 10
        """)

        sample = cursor.fetchall()

        print()
        print("Sample employees:")

        for employee in sample:

            print(
                f"{employee['employee_id']} | "
                f"{employee['first_name']} "
                f"{employee['last_name']} | "
                f"{employee['department']} | "
                f"{employee['job_title']} | "
                f"K{employee['salary']:,.2f} | "
                f"{employee['employment_status']}"
            )

        print()
        print("✓ Employee table successfully populated.")

    except Error as e:

        print()
        print(f"MySQL Error: {e}")

    except Exception as e:

        print()
        print(f"Unexpected Error: {e}")

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

        print()
        print("=" * 70)
        print("KWACHA BANK EMPLOYEE GENERATION FINISHED")
        print("=" * 70)


if __name__ == "__main__":
    main()