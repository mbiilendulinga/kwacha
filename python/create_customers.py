import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import random
import math
from collections import Counter


# ============================================================
# KWACHA BANK - CUSTOMER GENERATOR
# ============================================================
#
# Purpose:
#   Generate a realistic synthetic Zambian customer population
#   and insert it into the MySQL "customers" table.
#
# IMPORTANT:
#   This script generates the relatively CLEAN base dataset.
#   We will deliberately introduce data-quality problems later
#   using a separate script.
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

NUM_CUSTOMERS = 10_000

# Fixed seed = reproducible dataset
RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)

REFERENCE_DATE = date(2026, 8, 13)


# ============================================================
# ZAMBIAN FIRST NAMES
# ============================================================
#
# These are deliberately larger than the prototype list.
# They include names commonly encountered in Zambia as well
# as names used across different naming traditions.
#
# The generator does NOT assume that every name is equally
# common.
# ============================================================

MALE_FIRST_NAMES = [
    "Andrew", "Anthony", "Arthur", "Banda", "Blessing",
    "Brian", "Bruce", "Bwalya", "Chanda", "Charles",
    "Chibale", "Chileshe", "Chilufya", "Chisala", "Chisanga",
    "Chishimba", "Chisomo", "Chitundu", "Christopher", "Chomba",
    "Daniel", "David", "Dennis", "Derrick", "Douglas",
    "Edgar", "Edward", "Elijah", "Emmanuel", "Eric",
    "Esther", "Felix", "Francis", "Frank", "Gabriel",
    "Gift", "Godfrey", "Grace", "Harrison", "Isaac",
    "Jackson", "Jacob", "James", "Jason", "John",
    "Jonathan", "Joseph", "Joshua", "Justin", "Kabwe",
    "Kaleb", "Kalunga", "Kangwa", "Kennedy", "Kelvin",
    "Kenny", "Kinsley", "Kondwani", "Kunda", "Lawrence",
    "Lazarus", "Levi", "Lewis", "Lloyd", "Lubinda",
    "Lucas", "Lackson", "Martin", "Matthew", "Michael",
    "Moses", "Mubanga", "Mulenga", "Mumba", "Mwamba",
    "Mutale", "Nathan", "Nathaniel", "Nicholas", "Nicolas",
    "Ngosa", "Nkoloma", "Patrick", "Paul", "Peter",
    "Philemon", "Raphael", "Reuben", "Richard", "Robert",
    "Ruben", "Samuel", "Saviour", "Sebastian", "Shadreck",
    "Simon", "Stanley", "Stephen", "Steven", "Tapiwa",
    "Thomas", "Trevor", "Victor", "Vincent", "Wesley",
    "William", "Wilson", "Yoram", "Zachariah"
]


FEMALE_FIRST_NAMES = [
    "Alice", "Amanda", "Angela", "Annie", "Beatrice",
    "Belinda", "Blessing", "Brenda", "Bridget", "Bwalya",
    "Chanda", "Chantal", "Charity", "Chileshe", "Chilufya",
    "Chipo", "Chisomo", "Chitalu", "Chizoba", "Christine",
    "Cynthia", "Daisy", "Diana", "Dorcas", "Doreen",
    "Edith", "Ellen", "Emmanuella", "Esther", "Faith",
    "Florence", "Frances", "Gabriella", "Gift", "Gladys",
    "Gloria", "Grace", "Hannah", "Hope", "Ireen",
    "Irene", "Ivy", "Janet", "Jennifer", "Jessica",
    "Joan", "Joy", "Joyce", "Judith", "Juliet",
    "Kabwe", "Kali", "Kangwa", "Karen", "Katherine",
    "Kawama", "Kondwani", "Lillian", "Linda", "Lois",
    "Loveness", "Lucy", "Lydia", "Maggie", "Martha",
    "Mary", "Mercy", "Memory", "Michelle", "Mildred",
    "Monica", "Mutinta", "Mwaka", "Mwape", "Mwamba",
    "Namatama", "Naomi", "Natasha", "Nchimunya", "Nkandu",
    "Noria", "Patience", "Pauline", "Peace", "Precious",
    "Princess", "Rachel", "Regina", "Rose", "Ruth",
    "Sarah", "Sharon", "Sophia", "Susan", "Tabitha",
    "Tamara", "Tasha", "Thandiwe", "Tionenji", "Veronica",
    "Victoria", "Winnie", "Yvonne", "Zainabu", "Zambia"
]


# ============================================================
# ZAMBIAN SURNAMES
# ============================================================
#
# We intentionally have many surnames to reduce repetitive
# combinations when we scale the dataset.
# ============================================================

SURNAMES = [
    "Banda",
    "Bwalya",
    "Chanda",
    "Chibwe",
    "Chilufya",
    "Chimbala",
    "Chirwa",
    "Chisala",
    "Chishimba",
    "Chisanga",
    "Chitembo",
    "Chitundu",
    "Chomba",
    "Chungu",
    "Kabaso",
    "Kabwe",
    "Kalaba",
    "Kalunga",
    "Kangwa",
    "Kapasa",
    "Kapembwa",
    "Kasonde",
    "Katanga",
    "Katongo",
    "Kaunda",
    "Kayanda",
    "Kunda",
    "Lungu",
    "Mambwe",
    "Manda",
    "Mbewe",
    "Mfula",
    "Michelo",
    "Milambo",
    "Moyo",
    "Mulenga",
    "Mumba",
    "Mungala",
    "Munkombwe",
    "Munthali",
    "Musonda",
    "Mwamba",
    "Mwansa",
    "Mweemba",
    "Mwewa",
    "Mwila",
    "Mwikisa",
    "Mwelwa",
    "Nasilele",
    "Ng'andu",
    "Ngoma",
    "Ngosa",
    "Nkole",
    "Nkonde",
    "Nkombo",
    "Nsofwa",
    "Nyirenda",
    "Phiri",
    "Sakala",
    "Sampa",
    "Sichone",
    "Simfukwe",
    "Simukonda",
    "Simwanza",
    "Sinkala",
    "Soko",
    "Tembo",
    "Zimba",
    "Zulu",
    "Mukuka",
    "Munkonge",
    "Mushota",
    "Muyanga",
    "Muzala",
    "Chilongo",
    "Chitapi",
    "Chizhyuka",
    "Chongwe",
    "Kanyama",
    "Katembo",
    "Lukwesa",
    "Lumamba",
    "Lusambo",
    "Mubita",
    "Muleya",
    "Mulenga",
    "Mumba",
    "Musuku",
    "Mwape",
    "Mwewa",
    "Nkhata",
    "Nkhoma",
    "Phiri",
    "Sichamba",
    "Sikazwe",
    "Sikombe",
    "Sinyangwe",
    "Tembo",
    "Yeta"
]


# ============================================================
# ZAMBIAN GEOGRAPHY
# ============================================================
#
# Province -> District -> City/Town
#
# We use weighted province selection separately.
# ============================================================

LOCATIONS = {

    "Central": [
        ("Chibombo", "Chibombo"),
        ("Kabwe", "Kabwe"),
        ("Kapiri Mposhi", "Kapiri Mposhi"),
        ("Mkushi", "Mkushi"),
        ("Mumbwa", "Mumbwa"),
        ("Serenje", "Serenje")
    ],

    "Copperbelt": [
        ("Chililabombwe", "Chililabombwe"),
        ("Chingola", "Chingola"),
        ("Kalulushi", "Kalulushi"),
        ("Kitwe", "Kitwe"),
        ("Luanshya", "Luanshya"),
        ("Mufulira", "Mufulira"),
        ("Ndola", "Ndola")
    ],

    "Eastern": [
        ("Chipata", "Chipata"),
        ("Katete", "Katete"),
        ("Lundazi", "Lundazi"),
        ("Mambwe", "Mambwe"),
        ("Nyimba", "Nyimba"),
        ("Petauke", "Petauke")
    ],

    "Luapula": [
        ("Kawambwa", "Kawambwa"),
        ("Mansa", "Mansa"),
        ("Mwense", "Mwense"),
        ("Nchelenge", "Nchelenge"),
        ("Samfya", "Samfya")
    ],

    "Lusaka": [
        ("Chongwe", "Chongwe"),
        ("Kafue", "Kafue"),
        ("Luangwa", "Luangwa"),
        ("Lusaka", "Lusaka")
    ],

    "Muchinga": [
        ("Chinsali", "Chinsali"),
        ("Isoka", "Isoka"),
        ("Mpika", "Mpika"),
        ("Nakonde", "Nakonde")
    ],

    "Northern": [
        ("Kasama", "Kasama"),
        ("Luwingu", "Luwingu"),
        ("Mbala", "Mbala"),
        ("Mporokoso", "Mporokoso"),
        ("Mungwi", "Mungwi")
    ],

    "North-Western": [
        ("Chavuma", "Chavuma"),
        ("Kasempa", "Kasempa"),
        ("Mufumbwe", "Mufumbwe"),
        ("Mwinilunga", "Mwinilunga"),
        ("Solwezi", "Solwezi"),
        ("Zambezi", "Zambezi")
    ],

    "Southern": [
        ("Chikankata", "Chikankata"),
        ("Choma", "Choma"),
        ("Kalomo", "Kalomo"),
        ("Livingstone", "Livingstone"),
        ("Mazabuka", "Mazabuka"),
        ("Monze", "Monze"),
        ("Pemba", "Pemba"),
        ("Siavonga", "Siavonga")
    ],

    "Western": [
        ("Kalabo", "Kalabo"),
        ("Kaoma", "Kaoma"),
        ("Limulunga", "Limulunga"),
        ("Mongu", "Mongu"),
        ("Senanga", "Senanga"),
        ("Sesheke", "Sesheke")
    ]
}


# ============================================================
# PROVINCE DISTRIBUTION
# ============================================================
#
# These are modeled banking-customer proportions, NOT a claim
# about exact population census proportions.
#
# Lusaka and Copperbelt receive higher representation because
# they contain major urban/commercial banking centers.
# ============================================================

PROVINCE_WEIGHTS = [
    ("Lusaka", 0.30),
    ("Copperbelt", 0.19),
    ("Central", 0.10),
    ("Southern", 0.10),
    ("Eastern", 0.09),
    ("Northern", 0.07),
    ("North-Western", 0.06),
    ("Western", 0.04),
    ("Luapula", 0.03),
    ("Muchinga", 0.02)
]


# ============================================================
# OCCUPATIONS
# ============================================================

EMPLOYED_OCCUPATIONS = [

    ("Teacher", "Government", 0.09),
    ("Nurse", "Government", 0.055),
    ("Doctor", "Government", 0.008),
    ("Accountant", "Private", 0.045),
    ("Banking Officer", "Private", 0.035),
    ("Data Analyst", "Private", 0.015),
    ("Software Developer", "Private", 0.015),
    ("Engineer", "Private", 0.025),
    ("Sales Officer", "Private", 0.055),
    ("Administrative Officer", "Private", 0.06),
    ("Human Resources Officer", "Private", 0.025),
    ("Police Officer", "Government", 0.025),
    ("Military Personnel", "Government", 0.02),
    ("Civil Servant", "Government", 0.09),
    ("Lawyer", "Private", 0.012),
    ("Lecturer", "Government", 0.012),
    ("Pharmacist", "Private", 0.015),
    ("Technician", "Private", 0.04),
    ("Driver", "Private", 0.055),
    ("Electrician", "Private", 0.025),
    ("Construction Worker", "Private", 0.04),
    ("Marketing Officer", "Private", 0.03),
    ("Procurement Officer", "Private", 0.025),
    ("Operations Officer", "Private", 0.035),
    ("Manager", "Private", 0.02),
    ("Other Professional", "Private", 0.15)
]


# ============================================================
# SELF-EMPLOYED OCCUPATIONS
# ============================================================

SELF_EMPLOYED_OCCUPATIONS = [

    ("Retail Business Owner", 0.20),
    ("Trader", 0.12),
    ("Farmer", 0.13),
    ("Transport Operator", 0.07),
    ("Contractor", 0.07),
    ("Restaurant Owner", 0.05),
    ("Consultant", 0.05),
    ("Real Estate Business Owner", 0.03),
    ("Small Manufacturer", 0.03),
    ("Professional Services", 0.08),
    ("Other Business Owner", 0.17)
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def weighted_choice(items):
    """
    Select one item from:

        [(value, weight), ...]

    using weighted random selection.
    """

    values = [item[0] for item in items]
    weights = [item[1] for item in items]

    return random.choices(
        values,
        weights=weights,
        k=1
    )[0]


def random_date(start_date, end_date):

    if start_date > end_date:
        return end_date

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days)
    )


def calculate_age(dob):

    age = REFERENCE_DATE.year - dob.year

    if (
        REFERENCE_DATE.month,
        REFERENCE_DATE.day
    ) < (
        dob.month,
        dob.day
    ):
        age -= 1

    return age


# ============================================================
# NAME GENERATION
# ============================================================

def generate_name(gender):

    if gender == "Male":
        first_name = random.choice(MALE_FIRST_NAMES)
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)

    last_name = random.choice(SURNAMES)

    return first_name, last_name


# ============================================================
# DATE OF BIRTH
# ============================================================

def generate_dob():

    # Banking customers must be adults in this dataset.
    #
    # We use a slightly weighted age distribution rather than
    # making every age from 18-80 equally likely.

    age = weighted_choice([

        (18, 0.015),
        (19, 0.015),
        (20, 0.018),
        (21, 0.020),
        (22, 0.022),

        (23, 0.025),
        (24, 0.025),
        (25, 0.030),
        (26, 0.030),
        (27, 0.030),
        (28, 0.030),
        (29, 0.030),

        (30, 0.032),
        (31, 0.032),
        (32, 0.032),
        (33, 0.032),
        (34, 0.032),

        (35, 0.030),
        (36, 0.030),
        (37, 0.030),
        (38, 0.030),
        (39, 0.030),

        (40, 0.028),
        (41, 0.028),
        (42, 0.028),
        (43, 0.028),
        (44, 0.028),

        (45, 0.025),
        (46, 0.025),
        (47, 0.025),
        (48, 0.025),
        (49, 0.025),

        (50, 0.022),
        (51, 0.022),
        (52, 0.022),
        (53, 0.022),
        (54, 0.022),

        (55, 0.018),
        (56, 0.018),
        (57, 0.018),
        (58, 0.018),
        (59, 0.018),

        (60, 0.015),
        (61, 0.015),
        (62, 0.015),
        (63, 0.015),
        (64, 0.015),

        (65, 0.012),
        (66, 0.012),
        (67, 0.012),
        (68, 0.012),
        (69, 0.012),

        (70, 0.009),
        (71, 0.009),
        (72, 0.009),
        (73, 0.009),
        (74, 0.009),

        (75, 0.006),
        (76, 0.006),
        (77, 0.006),
        (78, 0.006),
        (79, 0.006),
        (80, 0.006)
    ])

    start = date(
        REFERENCE_DATE.year - age - 1,
        REFERENCE_DATE.month,
        REFERENCE_DATE.day
    )

    end = date(
        REFERENCE_DATE.year - age,
        REFERENCE_DATE.month,
        REFERENCE_DATE.day
    )

    return random_date(start, end)


# ============================================================
# EMPLOYMENT
# ============================================================

def determine_employment(age):

    if age <= 22:

        return weighted_choice([
            ("Student", 0.42),
            ("Employed", 0.28),
            ("Self-employed", 0.10),
            ("Unemployed", 0.20)
        ])

    elif age <= 30:

        return weighted_choice([
            ("Employed", 0.56),
            ("Self-employed", 0.18),
            ("Unemployed", 0.20),
            ("Student", 0.06)
        ])

    elif age <= 45:

        return weighted_choice([
            ("Employed", 0.58),
            ("Self-employed", 0.25),
            ("Unemployed", 0.12),
            ("Other", 0.05)
        ])

    elif age <= 55:

        return weighted_choice([
            ("Employed", 0.55),
            ("Self-employed", 0.27),
            ("Unemployed", 0.10),
            ("Other", 0.08)
        ])

    elif age <= 64:

        return weighted_choice([
            ("Employed", 0.35),
            ("Self-employed", 0.25),
            ("Retired", 0.30),
            ("Unemployed", 0.10)
        ])

    else:

        return weighted_choice([
            ("Retired", 0.70),
            ("Self-employed", 0.10),
            ("Unemployed", 0.15),
            ("Other", 0.05)
        ])


# ============================================================
# OCCUPATION
# ============================================================

def determine_occupation(employment_status):

    if employment_status == "Student":
        return "Student", "Not Applicable"

    if employment_status == "Unemployed":
        return "Unemployed", "Not Applicable"

    if employment_status == "Retired":
        return "Retired", "Not Applicable"

    if employment_status == "Other":
        return "Other", "Not Applicable"

    if employment_status == "Self-employed":

        occupation = weighted_choice(
            SELF_EMPLOYED_OCCUPATIONS
        )

        return occupation, "Self-employed"

    selected = random.choices(
        EMPLOYED_OCCUPATIONS,
        weights=[item[2] for item in EMPLOYED_OCCUPATIONS],
        k=1
    )[0]

    return selected[0], selected[1]


# ============================================================
# INCOME
# ============================================================

def determine_income(
    age,
    employment_status,
    occupation
):

    if employment_status == "Student":

        return round(
            random.triangular(
                0,
                8000,
                2500
            ),
            2
        )

    if employment_status == "Unemployed":

        return round(
            random.triangular(
                0,
                5000,
                1000
            ),
            2
        )

    if employment_status == "Retired":

        return round(
            random.triangular(
                4000,
                35000,
                10000
            ),
            2
        )

    if employment_status == "Self-employed":

        # Log-normal distribution:
        # many small/medium businesses,
        # fewer extremely high earners.

        income = random.lognormvariate(
            math.log(16_000),
            0.75
        )

        income = max(
            2_500,
            min(income, 300_000)
        )

        return round(income, 2)

    # --------------------------------------------------------
    # FORMAL EMPLOYMENT
    # --------------------------------------------------------

    income_ranges = {

        "Doctor": (30_000, 150_000),
        "Lawyer": (20_000, 100_000),
        "Lecturer": (18_000, 65_000),
        "Engineer": (15_000, 75_000),
        "Software Developer": (12_000, 70_000),
        "Data Analyst": (10_000, 55_000),
        "Manager": (20_000, 100_000),
        "Banking Officer": (9_000, 50_000),
        "Accountant": (9_000, 50_000),
        "Pharmacist": (10_000, 55_000),
        "Nurse": (7_000, 32_000),
        "Teacher": (6_000, 30_000),
        "Civil Servant": (6_000, 32_000),
        "Police Officer": (6_000, 27_000),
        "Military Personnel": (6_000, 28_000),
        "Driver": (4_500, 16_000),
        "Construction Worker": (4_500, 20_000),
        "Electrician": (5_000, 22_000),
        "Technician": (6_000, 25_000)
    }

    if occupation in income_ranges:

        low, high = income_ranges[occupation]

        income = random.triangular(
            low,
            high,
            low + ((high - low) * 0.35)
        )

    else:

        income = random.lognormvariate(
            math.log(12_000),
            0.60
        )

        income = max(
            4_500,
            min(income, 120_000)
        )

    # Experience effect
    if age >= 40:
        income *= random.uniform(
            1.00,
            1.18
        )

    return round(income, 2)


# ============================================================
# MARITAL STATUS
# ============================================================

def determine_marital_status(age):

    if age <= 22:

        return weighted_choice([
            ("Single", 0.90),
            ("Married", 0.08),
            ("Divorced", 0.01),
            ("Widowed", 0.01)
        ])

    if age <= 30:

        return weighted_choice([
            ("Single", 0.60),
            ("Married", 0.35),
            ("Divorced", 0.04),
            ("Widowed", 0.01)
        ])

    if age <= 45:

        return weighted_choice([
            ("Married", 0.64),
            ("Single", 0.22),
            ("Divorced", 0.11),
            ("Widowed", 0.03)
        ])

    if age <= 60:

        return weighted_choice([
            ("Married", 0.62),
            ("Single", 0.12),
            ("Divorced", 0.16),
            ("Widowed", 0.10)
        ])

    return weighted_choice([
        ("Married", 0.48),
        ("Single", 0.08),
        ("Divorced", 0.12),
        ("Widowed", 0.32)
    ])


# ============================================================
# DEPENDENTS
# ============================================================

def determine_dependents(
    age,
    marital_status
):

    if age < 23:

        return weighted_choice([
            (0, 0.85),
            (1, 0.10),
            (2, 0.05)
        ])

    if age < 30:

        return weighted_choice([
            (0, 0.35),
            (1, 0.30),
            (2, 0.23),
            (3, 0.12)
        ])

    if age < 45:

        return weighted_choice([
            (0, 0.08),
            (1, 0.17),
            (2, 0.27),
            (3, 0.25),
            (4, 0.15),
            (5, 0.08)
        ])

    if age < 60:

        return weighted_choice([
            (0, 0.10),
            (1, 0.15),
            (2, 0.22),
            (3, 0.23),
            (4, 0.16),
            (5, 0.09),
            (6, 0.05)
        ])

    return weighted_choice([
        (0, 0.25),
        (1, 0.25),
        (2, 0.25),
        (3, 0.17),
        (4, 0.08)
    ])


# ============================================================
# RISK
# ============================================================

def determine_risk(
    age,
    employment_status,
    income,
    dependents
):

    score = 0

    if employment_status == "Unemployed":
        score += 3

    elif employment_status == "Self-employed":
        score += 1

    elif employment_status == "Student":
        score += 1

    elif employment_status == "Retired":
        score += 1

    if income is not None:

        if income < 5_000:
            score += 3

        elif income < 10_000:
            score += 2

        elif income < 20_000:
            score += 1

    if dependents >= 5:
        score += 2

    elif dependents >= 3:
        score += 1

    if age < 23:
        score += 1

    if score >= 5:

        return weighted_choice([
            ("High", 0.65),
            ("Medium", 0.30),
            ("Low", 0.05)
        ])

    if score >= 3:

        return weighted_choice([
            ("Medium", 0.60),
            ("Low", 0.30),
            ("High", 0.10)
        ])

    return weighted_choice([
        ("Low", 0.72),
        ("Medium", 0.25),
        ("High", 0.03)
    ])


# ============================================================
# CUSTOMER SEGMENT
# ============================================================

def determine_segment(
    age,
    employment_status,
    income
):

    if age <= 24:
        return "Youth"

    if employment_status == "Student":
        return "Youth"

    if employment_status == "Self-employed":
        return "Business"

    if income is None:
        return "Mass Market"

    if income >= 50_000:
        return "Affluent"

    if income >= 20_000:
        return "Mass Affluent"

    if income >= 8_000:
        return "Mass Market"

    return "Entry Level"


# ============================================================
# KYC
# ============================================================

def determine_kyc():

    return weighted_choice([
        ("Verified", 0.92),
        ("Pending", 0.05),
        ("Review Required", 0.02),
        ("Incomplete", 0.01)
    ])


# ============================================================
# CUSTOMER TENURE
# ============================================================

def determine_customer_since(dob):
    """
    Determine a realistic date when the customer joined Kwacha Bank.

    Customers must be at least 18 when they become customers.
    Handles February 29 birthdays correctly.
    """

    # Calculate 18th birthday safely
    try:
        eighteenth_birthday = date(
            dob.year + 18,
            dob.month,
            dob.day
        )
    except ValueError:
        # Handles February 29 birthdays in non-leap years
        eighteenth_birthday = date(
            dob.year + 18,
            2,
            28
        )

    # Bank dataset period
    dataset_start = date(2018, 1, 1)
    dataset_end = date(2026, 8, 13)

    # Customer cannot join before their 18th birthday
    earliest_possible = max(
        eighteenth_birthday,
        dataset_start
    )

    # If the customer only recently became 18,
    # their customer_since should be close to their birthday.
    available_days = (dataset_end - earliest_possible).days

    if available_days <= 0:
        return earliest_possible

    # Most customers don't necessarily join immediately at 18.
    # Pick a random date between their 18th birthday and dataset end.
    customer_since = earliest_possible + timedelta(
        days=random.randint(0, available_days)
    )

    return customer_since


# ============================================================
# GENERATE ONE CUSTOMER
# ============================================================

def generate_customer(customer_number):

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    gender = weighted_choice([
        ("Male", 0.49),
        ("Female", 0.51)
    ])

    first_name, last_name = generate_name(
        gender
    )

    # --------------------------------------------------------
    # Birth
    # --------------------------------------------------------

    dob = generate_dob()

    age = calculate_age(dob)

    # --------------------------------------------------------
    # Geography
    # --------------------------------------------------------

    province = weighted_choice(
        PROVINCE_WEIGHTS
    )

    district, city = random.choice(
        LOCATIONS[province]
    )

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    employment_status = determine_employment(
        age
    )

    occupation, employer_type = determine_occupation(
        employment_status
    )

    # --------------------------------------------------------
    # Income
    # --------------------------------------------------------

    monthly_income = determine_income(
        age,
        employment_status,
        occupation
    )

    # --------------------------------------------------------
    # Family
    # --------------------------------------------------------

    marital_status = determine_marital_status(
        age
    )

    dependents = determine_dependents(
        age,
        marital_status
    )

    # --------------------------------------------------------
    # Customer history
    # --------------------------------------------------------

    customer_since = determine_customer_since(
        dob
    )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    risk_rating = determine_risk(
        age,
        employment_status,
        monthly_income,
        dependents
    )

    # --------------------------------------------------------
    # KYC
    # --------------------------------------------------------

    kyc_status = determine_kyc()

    # --------------------------------------------------------
    # Segment
    # --------------------------------------------------------

    customer_segment = determine_segment(
        age,
        employment_status,
        monthly_income
    )

    # --------------------------------------------------------
    # Active status
    # --------------------------------------------------------

    is_active = random.choices(
        [True, False],
        weights=[0.94, 0.06],
        k=1
    )[0]

    # --------------------------------------------------------
    # SMALL AMOUNT OF NATURAL MISSINGNESS
    #
    # This is NOT the main dirty-data stage.
    # These are just realistic optional-field gaps.
    # --------------------------------------------------------

    if random.random() < 0.01:
        occupation = None

    if random.random() < 0.008:
        employer_type = None

    if random.random() < 0.006:
        monthly_income = None

    if random.random() < 0.005:
        marital_status = None

    # --------------------------------------------------------
    # Customer ID
    # --------------------------------------------------------

    customer_id = (
        f"CUST{customer_number:07d}"
    )

    return (
        customer_id,
        first_name,
        last_name,
        dob,
        gender,
        "Zambian",
        province,
        district,
        employment_status,
        occupation,
        employer_type,
        monthly_income,
        customer_since,
        marital_status,
        dependents,
        risk_rating,
        kyc_status,
        customer_segment,
        is_active
    )


# ============================================================
# VALIDATION REPORT
# ============================================================

def print_generation_report(customers):

    print("\n")
    print("=" * 70)
    print("LOCAL GENERATION VALIDATION")
    print("=" * 70)

    print(
        f"\nRows generated: {len(customers):,}"
    )

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    gender_counter = Counter(
        row[4] for row in customers
    )

    print("\nGender:")

    for key, value in gender_counter.most_common():

        percentage = (
            value / len(customers)
        ) * 100

        print(
            f"  {key:10} "
            f"{value:6,} "
            f"({percentage:5.2f}%)"
        )

    # --------------------------------------------------------
    # Province
    # --------------------------------------------------------

    province_counter = Counter(
        row[6] for row in customers
    )

    print("\nProvince:")

    for key, value in province_counter.most_common():

        percentage = (
            value / len(customers)
        ) * 100

        print(
            f"  {key:15} "
            f"{value:6,} "
            f"({percentage:5.2f}%)"
        )

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    employment_counter = Counter(
        row[8] for row in customers
    )

    print("\nEmployment status:")

    for key, value in employment_counter.most_common():

        percentage = (
            value / len(customers)
        ) * 100

        print(
            f"  {key:15} "
            f"{value:6,} "
            f"({percentage:5.2f}%)"
        )

    # --------------------------------------------------------
    # Segments
    # --------------------------------------------------------

    segment_counter = Counter(
        row[17] for row in customers
    )

    print("\nCustomer segments:")

    for key, value in segment_counter.most_common():

        percentage = (
            value / len(customers)
        ) * 100

        print(
            f"  {key:15} "
            f"{value:6,} "
            f"({percentage:5.2f}%)"
        )

    # --------------------------------------------------------
    # Names
    # --------------------------------------------------------

    full_names = [
        f"{row[1]} {row[2]}"
        for row in customers
    ]

    unique_names = len(
        set(full_names)
    )

    print("\nName diversity:")

    print(
        f"  Unique full names: "
        f"{unique_names:,}"
    )

    print(
        f"  Duplicate full-name rows: "
        f"{len(full_names) - unique_names:,}"
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\nMissing values:")

    fields = {
        "occupation": 9,
        "employer_type": 10,
        "monthly_income": 11,
        "marital_status": 13
    }

    for field, index in fields.items():

        missing = sum(
            1
            for row in customers
            if row[index] is None
        )

        percentage = (
            missing / len(customers)
        ) * 100

        print(
            f"  {field:20} "
            f"{missing:5,} "
            f"({percentage:5.2f}%)"
        )


# ============================================================
# INSERT INTO MYSQL
# ============================================================

def insert_customers(customers):

    connection = None
    cursor = None

    try:

        print("\n")
        print("=" * 70)
        print("CONNECTING TO MYSQL")
        print("=" * 70)

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()

        sql = """
            INSERT INTO customers (

                customer_id,
                first_name,
                last_name,
                date_of_birth,
                gender,
                nationality,
                province,
                district,
                employment_status,
                occupation,
                employer_type,
                monthly_income,
                customer_since,
                marital_status,
                dependents,
                risk_rating,
                kyc_status,
                customer_segment,
                is_active

            )
            VALUES (

                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s

            )
        """

        batch_size = 1_000

        print(
            f"\nInserting "
            f"{len(customers):,} customers..."
        )

        for start in range(
            0,
            len(customers),
            batch_size
        ):

            batch = customers[
                start:start + batch_size
            ]

            cursor.executemany(
                sql,
                batch
            )

            connection.commit()

            completed = min(
                start + batch_size,
                len(customers)
            )

            percentage = (
                completed / len(customers)
            ) * 100

            print(
                f"  {completed:>8,} / "
                f"{len(customers):,} "
                f"({percentage:6.2f}%)"
            )

        # ----------------------------------------------------
        # Database verification
        # ----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM customers"
        )

        database_count = cursor.fetchone()[0]

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        print(
            f"\nCustomers currently in database: "
            f"{database_count:,}"
        )

        # ----------------------------------------------------
        # Average income
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                ROUND(AVG(monthly_income), 2)
            FROM customers
            WHERE monthly_income IS NOT NULL
        """)

        average_income = cursor.fetchone()[0]

        print(
            f"Average monthly income: "
            f"K{average_income:,.2f}"
        )

        # ----------------------------------------------------
        # Sample customers
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                customer_id,
                first_name,
                last_name,
                date_of_birth,
                gender,
                province,
                district,
                employment_status,
                occupation,
                monthly_income,
                customer_segment,
                risk_rating
            FROM customers
            ORDER BY customer_id
            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample customers:\n")

        for row in rows:

            print(
                f"{row[0]} | "
                f"{row[1]} {row[2]} | "
                f"{row[3]} | "
                f"{row[4]} | "
                f"{row[5]} | "
                f"{row[6]} | "
                f"{row[7]} | "
                f"{row[8]} | "
                f"K{row[9] if row[9] is not None else 0:,.2f} | "
                f"{row[10]} | "
                f"{row[11]}"
            )

        print("\n✓ Customer table successfully populated.")

    except Error as e:

        print("\nMYSQL ERROR:")
        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC CUSTOMER DATA GENERATOR")
    print("=" * 70)

    print(
        f"\nTarget customers: "
        f"{NUM_CUSTOMERS:,}"
    )

    print(
        f"Random seed: "
        f"{RANDOM_SEED}"
    )

    print(
        "\nGenerating customer population..."
    )

    customers = []

    for i in range(
        1,
        NUM_CUSTOMERS + 1
    ):

        customers.append(
            generate_customer(i)
        )

    print(
        "Generation completed."
    )

    # Local validation before touching MySQL
    print_generation_report(
        customers
    )

    # Insert
    insert_customers(
        customers
    )

    print("\n")
    print("=" * 70)
    print("KWACHA BANK CUSTOMER GENERATION FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()