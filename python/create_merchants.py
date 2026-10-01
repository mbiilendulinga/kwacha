import mysql.connector
from mysql.connector import Error
import random
from collections import Counter

# ============================================================
# KWACHA BANK
# SYNTHETIC MERCHANT DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813
TARGET_MERCHANTS = 5000

random.seed(RANDOM_SEED)


# ============================================================
# ZAMBIAN LOCATIONS
# ============================================================

LOCATIONS = [
    ("Lusaka", "Lusaka", "Lusaka", 30),
    ("Copperbelt", "Kitwe", "Kitwe", 11),
    ("Copperbelt", "Ndola", "Ndola", 10),
    ("Copperbelt", "Chingola", "Chingola", 6),
    ("Southern", "Livingstone", "Livingstone", 6),
    ("Southern", "Choma", "Choma", 4),
    ("Southern", "Mazabuka", "Mazabuka", 3),
    ("Central", "Kabwe", "Kabwe", 5),
    ("Central", "Kapiri Mposhi", "Kapiri Mposhi", 2),
    ("Eastern", "Chipata", "Chipata", 5),
    ("Eastern", "Petauke", "Petauke", 2),
    ("Northern", "Kasama", "Kasama", 4),
    ("Luapula", "Mansa", "Mansa", 3),
    ("North-Western", "Solwezi", "Solwezi", 5),
    ("Western", "Mongu", "Mongu", 2),
    ("Muchinga", "Chinsali", "Chinsali", 2),
    ("Muchinga", "Mpika", "Mpika", 2),
]


# ============================================================
# MERCHANT CATEGORIES
# ============================================================

MERCHANT_CATEGORIES = {
    "Supermarket": [
        "Supermarket",
        "Market",
        "Grocers",
        "Food Market"
    ],

    "Restaurant": [
        "Kitchen",
        "Restaurant",
        "Cafe",
        "Grill",
        "Takeaway"
    ],

    "Fuel Station": [
        "Fuel",
        "Service Station",
        "Filling Station"
    ],

    "Pharmacy": [
        "Pharmacy",
        "Chemist",
        "Health Pharmacy"
    ],

    "Clothing": [
        "Fashion",
        "Clothing",
        "Boutique",
        "Fashions"
    ],

    "Electronics": [
        "Electronics",
        "Tech",
        "Computers",
        "Digital",
        "Gadgets"
    ],

    "Hardware": [
        "Hardware",
        "Builders",
        "Building Supplies",
        "Home Supplies"
    ],

    "Hotel": [
        "Hotel",
        "Lodge",
        "Guest House",
        "Suites",
        "Resort"
    ],

    "Transport": [
        "Transport",
        "Taxi",
        "Logistics",
        "Travel",
        "Express"
    ],

    "School": [
        "School",
        "Academy",
        "College",
        "Institute"
    ],

    "Hospital": [
        "Medical Centre",
        "Hospital",
        "Clinic",
        "Health Centre"
    ],

    "Telecommunications": [
        "Telecom",
        "Communications",
        "Mobile Services",
        "Connect"
    ],

    "Professional Services": [
        "Consulting",
        "Accounting",
        "Legal Services",
        "Advisory",
        "Consultants"
    ],

    "Agriculture": [
        "Agro",
        "Farm Supplies",
        "Agri Services",
        "Agro Dealers"
    ],

    "Entertainment": [
        "Entertainment",
        "Lounge",
        "Events",
        "Cinema",
        "Club"
    ],

    "General Retail": [
        "Trading",
        "Enterprises",
        "General Dealers",
        "Traders",
        "Investments"
    ],
}


CATEGORY_WEIGHTS = {
    "Supermarket": 13,
    "Restaurant": 12,
    "Fuel Station": 9,
    "Pharmacy": 7,
    "Clothing": 8,
    "Electronics": 6,
    "Hardware": 7,
    "Hotel": 5,
    "Transport": 5,
    "School": 4,
    "Hospital": 3,
    "Telecommunications": 5,
    "Professional Services": 3,
    "Agriculture": 3,
    "Entertainment": 3,
    "General Retail": 10,
}


# ============================================================
# BUSINESS TYPES
# ============================================================

BUSINESS_TYPES = [
    ("Small Business", 52),
    ("Medium Business", 35),
    ("Large Business", 10),
    ("Corporate", 3),
]


# ============================================================
# NAME COMPONENTS
# ============================================================

ZAMBIAN_WORDS = [
    "Mwamba",
    "Manda",
    "Mwelwa",
    "Mulenga",
    "Mwansa",
    "Banda",
    "Chanda",
    "Phiri",
    "Zulu",
    "Tembo",
    "Kabwe",
    "Musonda",
    "Mumba",
    "Lungu",
    "Daka",
    "Kayanda",
    "Mubanga",
    "Chileshe",
    "Sinkala",
    "Sakala",
    "Kapasa",
    "Kunda",
    "Mbewe",
    "Sampa",
    "Chomba",
    "Mwanza",
    "Kalaba",
    "Milupi",
    "Chisala",
]


BUSINESS_WORDS = [
    "Premier",
    "Golden",
    "Royal",
    "Modern",
    "Bright",
    "First",
    "Trust",
    "Unity",
    "Eagle",
    "Victory",
    "Sunrise",
    "New Dawn",
    "Great",
    "Smart",
    "Prime",
    "Capital",
    "Central",
    "Express",
    "Classic",
    "Excellent",
]


# ============================================================
# HELPERS
# ============================================================

def weighted_choice(items):
    values = [item[0] for item in items]
    weights = [item[1] for item in items]

    return random.choices(
        values,
        weights=weights,
        k=1
    )[0]


def choose_location():

    values = LOCATIONS

    weights = [
        location[3]
        for location in LOCATIONS
    ]

    selected = random.choices(
        values,
        weights=weights,
        k=1
    )[0]

    province = selected[0]
    district = selected[1]
    city = selected[2]

    return province, district, city


def choose_category():

    categories = list(
        MERCHANT_CATEGORIES.keys()
    )

    weights = [
        CATEGORY_WEIGHTS[category]
        for category in categories
    ]

    return random.choices(
        categories,
        weights=weights,
        k=1
    )[0]


def generate_merchant_name(category, city):

    word1 = random.choice(
        ZAMBIAN_WORDS + BUSINESS_WORDS
    )

    word2 = random.choice(
        ZAMBIAN_WORDS + BUSINESS_WORDS
    )

    suffix = random.choice(
        MERCHANT_CATEGORIES[category]
    )

    patterns = [
        f"{word1} {suffix}",
        f"{word1} {word2} {suffix}",
        f"{word1} {word2}",
        f"{city} {word1} {suffix}",
        f"{word1} {city} {suffix}",
        f"{word1} {word2} Enterprises",
        f"{word1} Trading",
        f"{word1} Investments",
    ]

    return random.choice(patterns)


def introduce_messiness(value):

    if value is None:
        return None

    r = random.random()

    # 0.8% leading/trailing spaces
    if r < 0.008:
        return f" {value} "

    # 0.4% lowercase
    if r < 0.012:
        return value.lower()

    # 0.2% missing
    if r < 0.014:
        return None

    return value


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC MERCHANT DATA GENERATOR")
    print("=" * 70)

    print()
    print(f"Target merchants: {TARGET_MERCHANTS:,}")
    print(f"Random seed: {RANDOM_SEED}")

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # CONNECT
        # ----------------------------------------------------

        print()
        print("Connecting to MySQL...")

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("GENERATING MERCHANTS")
        print("=" * 70)

        merchants = []

        for i in range(
            1,
            TARGET_MERCHANTS + 1
        ):

            merchant_id = f"MER{i:07d}"

            province, district, city = choose_location()

            category = choose_category()

            merchant_name = generate_merchant_name(
                category,
                city
            )

            business_type = weighted_choice(
                BUSINESS_TYPES
            )

            merchant_name = introduce_messiness(
                merchant_name
            )

            # merchant_name is required by the database.
            # If the messiness algorithm removes it, restore a valid name.
            if merchant_name is None:
                merchant_name = generate_merchant_name(
                    category,
                    city
                )

            merchants.append(
                (
                    merchant_id,
                    merchant_name,
                    category,
                    province,
                    district,
                    city,
                    business_type
                )
            )

            if i % 1000 == 0:
                print(
                    f"  Generated "
                    f"{i:,} / "
                    f"{TARGET_MERCHANTS:,}"
                )

        print()
        print("Generation completed.")

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        category_counts = Counter(
            merchant[2]
            for merchant in merchants
        )

        province_counts = Counter(
            merchant[3]
            for merchant in merchants
        )

        business_counts = Counter(
            merchant[6]
            for merchant in merchants
        )

        missing_names = sum(
            1
            for merchant in merchants
            if merchant[1] is None
        )

        print()
        print(
            f"Merchants generated: "
            f"{len(merchants):,}"
        )

        print()
        print("Merchant categories:")

        for category, count in category_counts.most_common():

            print(
                f"  {category:<25} "
                f"{count:>5}"
            )

        print()
        print("Province distribution:")

        for province, count in province_counts.most_common():

            print(
                f"  {province:<18} "
                f"{count:>5}"
            )

        print()
        print("Business types:")

        for business_type, count in business_counts.most_common():

            print(
                f"  {business_type:<20} "
                f"{count:>5}"
            )

        print()
        print(
            f"Missing merchant names: "
            f"{missing_names}"
        )

        print()
        print("Sample merchants:")

        for merchant in merchants[:15]:

            print(
                f"{merchant[0]} | "
                f"{merchant[1]} | "
                f"{merchant[2]} | "
                f"{merchant[3]} | "
                f"{merchant[5]} | "
                f"{merchant[6]}"
            )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """
            INSERT INTO merchants (
                merchant_id,
                merchant_name,
                merchant_category,
                province,
                district,
                city,
                business_type
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s
            )
        """

        batch_size = 500

        for i in range(
            0,
            len(merchants),
            batch_size
        ):

            batch = merchants[
                i:i + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            processed = min(
                i + batch_size,
                len(merchants)
            )

            print(
                f"  {processed:,} / "
                f"{len(merchants):,} "
                f"({processed / len(merchants) * 100:6.2f}%)"
            )

        # ----------------------------------------------------
        # DATABASE VERIFICATION
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM merchants
        """)

        total = cursor.fetchone()["total"]

        print()
        print(
            f"Merchants currently in database: "
            f"{total:,}"
        )

        cursor.execute("""
            SELECT
                merchant_id,
                merchant_name,
                merchant_category,
                province,
                city,
                business_type
            FROM merchants
            ORDER BY merchant_id
            LIMIT 10
        """)

        sample = cursor.fetchall()

        print()
        print("Sample merchants:")

        for merchant in sample:

            print(
                f"{merchant['merchant_id']} | "
                f"{merchant['merchant_name']} | "
                f"{merchant['merchant_category']} | "
                f"{merchant['province']} | "
                f"{merchant['city']} | "
                f"{merchant['business_type']}"
            )

        print()
        print(
            "✓ Merchant table successfully populated."
        )

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
        print(
            "KWACHA BANK MERCHANT GENERATION FINISHED"
        )
        print("=" * 70)


if __name__ == "__main__":
    main()