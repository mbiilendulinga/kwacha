import mysql.connector
import pandas as pd
from mysql.connector import Error

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

OUTPUT_FILE = "kwacha_bank_data.xlsx"


def export_database():
    connection = None

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME
        )

        if not connection.is_connected():
            print("Could not connect to MySQL.")
            return

        print(f"Connected to database '{DB_NAME}'.")

        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()

        print(f"\nFound {len(tables)} tables.\n")

        with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

            for table in tables:
                print(f"Exporting: {table}")

                query = f"SELECT * FROM `{table}`"
                df = pd.read_sql(query, connection)

                df.to_excel(
                    writer,
                    sheet_name=table[:31],
                    index=False
                )

                print(f"  {len(df):,} rows exported.")

        print("\n" + "=" * 60)
        print("EXPORT COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nFile created: {OUTPUT_FILE}")
        print(f"Tables exported: {len(tables)}")

    except Error as e:
        print(f"\nMySQL Error: {e}")

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\nMySQL connection closed.")


if __name__ == "__main__":
    export_database()