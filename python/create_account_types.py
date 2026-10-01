import mysql.connector
from mysql.connector import Error


# ============================================================
# KWACHA BANK
# ACCOUNT TYPE DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"


# ============================================================
# ACCOUNT PRODUCTS
# ============================================================

ACCOUNT_TYPES = [

    {
        "account_type_id": "AT001",
        "account_name": "Basic Savings Account",
        "category": "Savings",
        "minimum_balance": 0,
        "monthly_fee": 0,
        "interest_rate": 2.50
    },

    {
        "account_type_id": "AT002",
        "account_name": "Premium Savings Account",
        "category": "Savings",
        "minimum_balance": 5000,
        "monthly_fee": 25,
        "interest_rate": 5.50
    },

    {
        "account_type_id": "AT003",
        "account_name": "Current Account",
        "category": "Current",
        "minimum_balance": 1000,
        "monthly_fee": 35,
        "interest_rate": 0
    },

    {
        "account_type_id": "AT004",
        "account_name": "Student Account",
        "category": "Savings",
        "minimum_balance": 0,
        "monthly_fee": 0,
        "interest_rate": 1.50
    },

    {
        "account_type_id": "AT005",
        "account_name": "Youth Account",
        "category": "Savings",
        "minimum_balance": 0,
        "monthly_fee": 0,
        "interest_rate": 2.00
    },

    {
        "account_type_id": "AT006",
        "account_name": "Salary Account",
        "category": "Current",
        "minimum_balance": 0,
        "monthly_fee": 15,
        "interest_rate": 0
    },

    {
        "account_type_id": "AT007",
        "account_name": "Business Current Account",
        "category": "Business",
        "minimum_balance": 5000,
        "monthly_fee": 75,
        "interest_rate": 0
    },

    {
        "account_type_id": "AT008",
        "account_name": "Business Savings Account",
        "category": "Business",
        "minimum_balance": 2500,
        "monthly_fee": 40,
        "interest_rate": 2.00
    },

    {
        "account_type_id": "AT009",
        "account_name": "Fixed Deposit Account",
        "category": "Investment",
        "minimum_balance": 10000,
        "monthly_fee": 0,
        "interest_rate": 8.50
    },

    {
        "account_type_id": "AT010",
        "account_name": "Premier Account",
        "category": "Premium",
        "minimum_balance": 25000,
        "monthly_fee": 100,
        "interest_rate": 9.00
    }

]


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
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("ACCOUNT TYPE DATA GENERATOR")
    print("=" * 70)

    print(f"\nAccount products: {len(ACCOUNT_TYPES)}")

    # --------------------------------------------------------
    # Display products
    # --------------------------------------------------------

    print("\nProducts to be created:\n")

    for account in ACCOUNT_TYPES:

        print(
            f"{account['account_type_id']} | "
            f"{account['account_name']:<28} | "
            f"{account['category']:<12} | "
            f"Minimum: K{account['minimum_balance']:,.2f} | "
            f"Fee: K{account['monthly_fee']:,.2f} | "
            f"Interest: {account['interest_rate']:.2f}%"
        )

    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------

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
            INSERT INTO account_types (
                account_type_id,
                account_name,
                category,
                minimum_balance,
                monthly_fee,
                interest_rate
            )
            VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """

        data = []

        for account in ACCOUNT_TYPES:

            data.append(
                (
                    account["account_type_id"],
                    account["account_name"],
                    account["category"],
                    account["minimum_balance"],
                    account["monthly_fee"],
                    account["interest_rate"]
                )
            )

        print(
            f"\nInserting {len(data)} account products..."
        )

        cursor.executemany(
            insert_sql,
            data
        )

        connection.commit()

        print(
            f"Successfully inserted "
            f"{cursor.rowcount} account products."
        )

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT COUNT(*)
            FROM account_types
        """)

        count = cursor.fetchone()[0]

        print(
            f"\nAccount types currently in database: {count}"
        )

        cursor.execute("""
            SELECT
                account_type_id,
                account_name,
                category,
                minimum_balance,
                monthly_fee,
                interest_rate
            FROM account_types
            ORDER BY account_type_id
        """)

        rows = cursor.fetchall()

        print("\nAccount products:\n")

        for row in rows:

            print(
                f"{row[0]} | "
                f"{row[1]:<28} | "
                f"{row[2]:<12} | "
                f"Min K{row[3]:,.2f} | "
                f"Fee K{row[4]:,.2f} | "
                f"{row[5]:.2f}%"
            )

        print(
            "\n✓ Account types successfully populated."
        )

    except Error as e:

        connection.rollback()

        print(f"\nMySQL Error: {e}")

    finally:

        cursor.close()
        connection.close()

    print("\n")
    print("=" * 70)
    print("KWACHA BANK ACCOUNT TYPE GENERATION FINISHED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()