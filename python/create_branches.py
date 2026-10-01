import mysql.connector
from mysql.connector import Error
from datetime import date
import random

# ============================================================
# KWACHA BANK
# SYNTHETIC BRANCH DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

random.seed(RANDOM_SEED)


# ============================================================
# ZAMBIAN BRANCH DATA
# ============================================================

BRANCHES = [

    # --------------------------------------------------------
    # LUSAKA
    # --------------------------------------------------------

    {
        "branch_name": "Cairo Road Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Longacres Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Manda Hill Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Woodlands Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Chilenje Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Kabulonga Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Chelstone Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Chawama Branch",
        "province": "Lusaka",
        "district": "Lusaka",
        "city": "Lusaka",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # COPPERBELT
    # --------------------------------------------------------

    {
        "branch_name": "Kitwe Main Branch",
        "province": "Copperbelt",
        "district": "Kitwe",
        "city": "Kitwe",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Ndola Main Branch",
        "province": "Copperbelt",
        "district": "Ndola",
        "city": "Ndola",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Kabwe Road Branch",
        "province": "Copperbelt",
        "district": "Ndola",
        "city": "Ndola",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Chingola Branch",
        "province": "Copperbelt",
        "district": "Chingola",
        "city": "Chingola",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Mufulira Branch",
        "province": "Copperbelt",
        "district": "Mufulira",
        "city": "Mufulira",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Luanshya Branch",
        "province": "Copperbelt",
        "district": "Luanshya",
        "city": "Luanshya",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # SOUTHERN
    # --------------------------------------------------------

    {
        "branch_name": "Livingstone Main Branch",
        "province": "Southern",
        "district": "Livingstone",
        "city": "Livingstone",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Choma Branch",
        "province": "Southern",
        "district": "Choma",
        "city": "Choma",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Mazabuka Branch",
        "province": "Southern",
        "district": "Mazabuka",
        "city": "Mazabuka",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Monze Branch",
        "province": "Southern",
        "district": "Monze",
        "city": "Monze",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # CENTRAL
    # --------------------------------------------------------

    {
        "branch_name": "Kabwe Main Branch",
        "province": "Central",
        "district": "Kabwe",
        "city": "Kabwe",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Kapiri Mposhi Branch",
        "province": "Central",
        "district": "Kapiri Mposhi",
        "city": "Kapiri Mposhi",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Mkushi Branch",
        "province": "Central",
        "district": "Mkushi",
        "city": "Mkushi",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # EASTERN
    # --------------------------------------------------------

    {
        "branch_name": "Chipata Main Branch",
        "province": "Eastern",
        "district": "Chipata",
        "city": "Chipata",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Petauke Branch",
        "province": "Eastern",
        "district": "Petauke",
        "city": "Petauke",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Katete Branch",
        "province": "Eastern",
        "district": "Katete",
        "city": "Katete",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # NORTHERN
    # --------------------------------------------------------

    {
        "branch_name": "Kasama Main Branch",
        "province": "Northern",
        "district": "Kasama",
        "city": "Kasama",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Mbala Branch",
        "province": "Northern",
        "district": "Mbala",
        "city": "Mbala",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # NORTH-WESTERN
    # --------------------------------------------------------

    {
        "branch_name": "Solwezi Main Branch",
        "province": "North-Western",
        "district": "Solwezi",
        "city": "Solwezi",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Mwinilunga Branch",
        "province": "North-Western",
        "district": "Mwinilunga",
        "city": "Mwinilunga",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Kasempa Branch",
        "province": "North-Western",
        "district": "Kasempa",
        "city": "Kasempa",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # WESTERN
    # --------------------------------------------------------

    {
        "branch_name": "Mongu Main Branch",
        "province": "Western",
        "district": "Mongu",
        "city": "Mongu",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Kaoma Branch",
        "province": "Western",
        "district": "Kaoma",
        "city": "Kaoma",
        "branch_type": "Retail",
    },

    {
        "branch_name": "Senanga Branch",
        "province": "Western",
        "district": "Senanga",
        "city": "Senanga",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # LUAPULA
    # --------------------------------------------------------

    {
        "branch_name": "Mansa Main Branch",
        "province": "Luapula",
        "district": "Mansa",
        "city": "Mansa",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Samfya Branch",
        "province": "Luapula",
        "district": "Samfya",
        "city": "Samfya",
        "branch_type": "Retail",
    },

    # --------------------------------------------------------
    # MUCHINGA
    # --------------------------------------------------------

    {
        "branch_name": "Chinsali Main Branch",
        "province": "Muchinga",
        "district": "Chinsali",
        "city": "Chinsali",
        "branch_type": "Full Service",
    },

    {
        "branch_name": "Mpika Branch",
        "province": "Muchinga",
        "district": "Mpika",
        "city": "Mpika",
        "branch_type": "Retail",
    },
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_opening_date(branch_type):
    """
    Generate a realistic opening date.

    Full-service branches tend to be older.
    Retail branches can be newer.
    """

    if branch_type == "Full Service":
        start_year = 2005
    else:
        start_year = 2010

    year = random.randint(start_year, 2025)
    month = random.randint(1, 12)

    # Avoid dates in the future
    if year == 2025:
        month = random.randint(1, 12)

    day = random.randint(1, 28)

    return date(year, month, day)


def generate_operating_cost(branch_type, city):
    """
    Generate monthly operating expenses.

    Larger urban branches cost more to operate.
    """

    if branch_type == "Full Service":
        base = random.uniform(180000, 350000)
    else:
        base = random.uniform(80000, 180000)

    # Lusaka and major commercial centres are more expensive.
    if city in ["Lusaka", "Kitwe", "Ndola", "Livingstone"]:
        base *= random.uniform(1.10, 1.35)

    return round(base, 2)


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
# MAIN GENERATOR
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC BRANCH DATA GENERATOR")
    print("=" * 70)

    print(f"\nTarget branches: {len(BRANCHES)}")
    print(f"Random seed: {RANDOM_SEED}")

    print("\nGenerating branch population...")

    generated_branches = []

    for index, branch in enumerate(BRANCHES, start=1):

        branch_id = f"BR{index:04d}"

        opening_date = random_opening_date(
            branch["branch_type"]
        )

        operating_cost = generate_operating_cost(
            branch["branch_type"],
            branch["city"]
        )

        generated_branches.append(
            (
                branch_id,
                branch["branch_name"],
                branch["province"],
                branch["district"],
                branch["city"],
                branch["branch_type"],
                opening_date,
                operating_cost
            )
        )

    print("Generation completed.")

    # ========================================================
    # LOCAL VALIDATION
    # ========================================================

    print("\n")
    print("=" * 70)
    print("LOCAL GENERATION VALIDATION")
    print("=" * 70)

    print(f"\nRows generated: {len(generated_branches)}")

    print("\nBranches by province:")

    province_counts = {}

    for branch in generated_branches:

        province = branch[2]

        province_counts[province] = (
            province_counts.get(province, 0) + 1
        )

    for province, count in province_counts.items():

        print(f"  {province:<18} {count:>2}")

    print("\nBranches by type:")

    type_counts = {}

    for branch in generated_branches:

        branch_type = branch[5]

        type_counts[branch_type] = (
            type_counts.get(branch_type, 0) + 1
        )

    for branch_type, count in type_counts.items():

        print(f"  {branch_type:<18} {count:>2}")

    # ========================================================
    # MYSQL
    # ========================================================

    print("\n")
    print("=" * 70)
    print("CONNECTING TO MYSQL")
    print("=" * 70)

    connection = connect_database()

    if connection is None:

        return

    cursor = connection.cursor()

    try:

        insert_sql = """
            INSERT INTO branches (
                branch_id,
                branch_name,
                province,
                district,
                city,
                branch_type,
                opening_date,
                monthly_operating_cost
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        print(f"\nInserting {len(generated_branches)} branches...")

        cursor.executemany(
            insert_sql,
            generated_branches
        )

        connection.commit()

        print(
            f"Successfully inserted "
            f"{cursor.rowcount} branches."
        )

        # ====================================================
        # DATABASE VERIFICATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute(
            "SELECT COUNT(*) FROM branches"
        )

        count = cursor.fetchone()[0]

        print(f"\nBranches currently in database: {count}")

        cursor.execute("""
            SELECT
                branch_id,
                branch_name,
                province,
                city,
                branch_type,
                opening_date,
                monthly_operating_cost
            FROM branches
            ORDER BY branch_id
            LIMIT 10
        """)

        rows = cursor.fetchall()

        print("\nSample branches:\n")

        for row in rows:

            print(
                f"{row[0]} | "
                f"{row[1]} | "
                f"{row[2]} | "
                f"{row[3]} | "
                f"{row[4]} | "
                f"{row[5]} | "
                f"K{row[6]:,.2f}"
            )

        print("\n✓ Branch table successfully populated.")

    except Error as e:

        connection.rollback()

        print(f"\nMySQL Error: {e}")

    finally:  

        cursor.close()
        connection.close()

    print("\n")
    print("=" * 70)
    print("KWACHA BANK BRANCH GENERATION FINISHED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()