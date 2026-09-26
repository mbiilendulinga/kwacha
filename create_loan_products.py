import mysql.connector
from mysql.connector import Error


# ============================================================
# KWACHA BANK
# LOAN PRODUCT DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"


# ============================================================
# LOAN PRODUCTS
# ============================================================

LOAN_PRODUCTS = [

    {
        "loan_product_id": "LP001",
        "product_name": "Personal Loan",
        "loan_category": "Personal",
        "minimum_amount": 5000,
        "maximum_amount": 150000,
        "base_interest_rate": 24.00,
        "maximum_term_months": 60,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP002",
        "product_name": "Salary Advance",
        "loan_category": "Personal",
        "minimum_amount": 1000,
        "maximum_amount": 30000,
        "base_interest_rate": 18.00,
        "maximum_term_months": 12,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP003",
        "product_name": "Emergency Loan",
        "loan_category": "Personal",
        "minimum_amount": 1000,
        "maximum_amount": 20000,
        "base_interest_rate": 22.00,
        "maximum_term_months": 12,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP004",
        "product_name": "Education Loan",
        "loan_category": "Education",
        "minimum_amount": 10000,
        "maximum_amount": 200000,
        "base_interest_rate": 16.00,
        "maximum_term_months": 60,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP005",
        "product_name": "Vehicle Loan",
        "loan_category": "Asset Finance",
        "minimum_amount": 30000,
        "maximum_amount": 500000,
        "base_interest_rate": 15.50,
        "maximum_term_months": 72,
        "collateral_required": True
    },

    {
        "loan_product_id": "LP006",
        "product_name": "Home Loan",
        "loan_category": "Mortgage",
        "minimum_amount": 150000,
        "maximum_amount": 3000000,
        "base_interest_rate": 13.50,
        "maximum_term_months": 240,
        "collateral_required": True
    },

    {
        "loan_product_id": "LP007",
        "product_name": "SME Business Loan",
        "loan_category": "Business",
        "minimum_amount": 25000,
        "maximum_amount": 1000000,
        "base_interest_rate": 19.50,
        "maximum_term_months": 60,
        "collateral_required": True
    },

    {
        "loan_product_id": "LP008",
        "product_name": "Business Working Capital",
        "loan_category": "Business",
        "minimum_amount": 10000,
        "maximum_amount": 500000,
        "base_interest_rate": 21.00,
        "maximum_term_months": 36,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP009",
        "product_name": "Agricultural Loan",
        "loan_category": "Agriculture",
        "minimum_amount": 10000,
        "maximum_amount": 750000,
        "base_interest_rate": 14.50,
        "maximum_term_months": 60,
        "collateral_required": True
    },

    {
        "loan_product_id": "LP010",
        "product_name": "Micro Enterprise Loan",
        "loan_category": "Microfinance",
        "minimum_amount": 1000,
        "maximum_amount": 100000,
        "base_interest_rate": 25.00,
        "maximum_term_months": 36,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP011",
        "product_name": "Overdraft Facility",
        "loan_category": "Credit Facility",
        "minimum_amount": 1000,
        "maximum_amount": 100000,
        "base_interest_rate": 28.00,
        "maximum_term_months": 12,
        "collateral_required": False
    },

    {
        "loan_product_id": "LP012",
        "product_name": "Premier Personal Loan",
        "loan_category": "Premium",
        "minimum_amount": 50000,
        "maximum_amount": 750000,
        "base_interest_rate": 13.00,
        "maximum_term_months": 84,
        "collateral_required": False
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
    print("LOAN PRODUCT DATA GENERATOR")
    print("=" * 70)

    print(f"\nLoan products: {len(LOAN_PRODUCTS)}")

    # --------------------------------------------------------
    # Display products
    # --------------------------------------------------------

    print("\nProducts to be created:\n")

    for product in LOAN_PRODUCTS:

        collateral = (
            "Required"
            if product["collateral_required"]
            else "Not Required"
        )

        print(
            f"{product['loan_product_id']} | "
            f"{product['product_name']:<28} | "
            f"{product['loan_category']:<16} | "
            f"K{product['minimum_amount']:,.0f}"
            f" - K{product['maximum_amount']:,.0f} | "
            f"{product['base_interest_rate']:.2f}% | "
            f"{product['maximum_term_months']} months | "
            f"Collateral: {collateral}"
        )

    # --------------------------------------------------------
    # Connect to MySQL
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
            INSERT INTO loan_products (
                loan_product_id,
                product_name,
                loan_category,
                minimum_amount,
                maximum_amount,
                base_interest_rate,
                maximum_term_months,
                collateral_required
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        data = []

        for product in LOAN_PRODUCTS:

            data.append(
                (
                    product["loan_product_id"],
                    product["product_name"],
                    product["loan_category"],
                    product["minimum_amount"],
                    product["maximum_amount"],
                    product["base_interest_rate"],
                    product["maximum_term_months"],
                    product["collateral_required"]
                )
            )

        print(
            f"\nInserting {len(data)} loan products..."
        )

        cursor.executemany(
            insert_sql,
            data
        )

        connection.commit()

        print(
            f"Successfully inserted "
            f"{cursor.rowcount} loan products."
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
            FROM loan_products
        """)

        count = cursor.fetchone()[0]

        print(
            f"\nLoan products currently in database: {count}"
        )

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
            ORDER BY loan_product_id
        """)

        rows = cursor.fetchall()

        print("\nLoan products:\n")

        for row in rows:

            collateral = (
                "Yes"
                if row[7]
                else "No"
            )

            print(
                f"{row[0]} | "
                f"{row[1]:<28} | "
                f"{row[2]:<16} | "
                f"K{row[3]:,.0f} - "
                f"K{row[4]:,.0f} | "
                f"{row[5]:.2f}% | "
                f"{row[6]} months | "
                f"Collateral: {collateral}"
            )

        print(
            "\n✓ Loan products successfully populated."
        )

    except Error as e:

        connection.rollback()

        print(f"\nMySQL Error: {e}")

    finally:

        cursor.close()
        connection.close()

    print("\n")
    print("=" * 70)
    print("KWACHA BANK LOAN PRODUCT GENERATION FINISHED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()