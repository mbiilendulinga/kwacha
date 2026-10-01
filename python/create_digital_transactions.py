import mysql.connector
from mysql.connector import Error
from decimal import Decimal
from datetime import datetime
import random
import string


# ============================================================
# KWACHA BANK
# SYNTHETIC DIGITAL TRANSACTION DATA GENERATOR
# ============================================================

DB_NAME = "kwacha_bank"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"

RANDOM_SEED = 20260813

# Percentage of eligible transactions that become digital
DIGITAL_RATE = 0.42


# ============================================================
# RANDOM GENERATOR
# ============================================================

random.seed(RANDOM_SEED)


# ============================================================
# ID GENERATOR
# ============================================================

def generate_id(prefix, length=12):

    characters = string.ascii_uppercase + string.digits

    random_part = "".join(
        random.choices(
            characters,
            k=length
        )
    )

    return f"{prefix}-{random_part}"


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
# DIGITAL CHANNEL LOGIC
# ============================================================

def choose_digital_channel(transaction):

    transaction_type = transaction["transaction_type"]
    amount = float(transaction["amount"])

    # Mobile banking dominates retail digital banking
    channels = [
        "Mobile Banking",
        "Mobile Banking",
        "Mobile Banking",
        "USSD",
        "Internet Banking",
        "Internet Banking",
        "Banking App"
    ]

    # Certain transactions are more likely to happen through
    # particular channels.

    if transaction_type in [
        "Bill Payment",
        "Airtime Purchase",
        "Mobile Money",
        "Transfer"
    ]:

        channels = [
            "Mobile Banking",
            "Mobile Banking",
            "USSD",
            "USSD",
            "Banking App"
        ]

    elif amount > 50000:

        channels = [
            "Internet Banking",
            "Internet Banking",
            "Banking App",
            "Mobile Banking"
        ]

    return random.choice(channels)


# ============================================================
# DEVICE TYPE
# ============================================================

def choose_device_type(channel):

    if channel == "USSD":

        return "Mobile Phone"

    if channel == "Internet Banking":

        return random.choices(
            [
                "Desktop",
                "Laptop",
                "Mobile Phone",
                "Tablet"
            ],
            weights=[
                30,
                25,
                40,
                5
            ],
            k=1
        )[0]

    return random.choices(
        [
            "Smartphone",
            "Tablet",
            "Mobile Phone"
        ],
        weights=[
            80,
            10,
            10
        ],
        k=1
    )[0]


# ============================================================
# OPERATING SYSTEM
# ============================================================

def choose_operating_system(device_type):

    if device_type in [
        "Mobile Phone",
        "Smartphone"
    ]:

        return random.choices(
            [
                "Android",
                "iOS",
                "KaiOS"
            ],
            weights=[
                72,
                25,
                3
            ],
            k=1
        )[0]

    if device_type == "Tablet":

        return random.choices(
            [
                "Android",
                "iOS"
            ],
            weights=[
                60,
                40
            ],
            k=1
        )[0]

    return random.choices(
        [
            "Windows",
            "macOS",
            "Linux"
        ],
        weights=[
            78,
            18,
            4
        ],
        k=1
    )[0]


# ============================================================
# IP COUNTRY
# ============================================================

def choose_ip_country():

    # Most transactions should originate from Zambia,
    # but international activity should exist.

    return random.choices(

        [
            "Zambia",
            "South Africa",
            "United Kingdom",
            "United States",
            "Zimbabwe",
            "Botswana",
            "Malawi",
            "Tanzania",
            "Kenya",
            "Other"
        ],

        weights=[
            92,
            2.0,
            1.2,
            1.0,
            0.8,
            0.5,
            0.5,
            0.4,
            0.4,
            1.2
        ],

        k=1
    )[0]


# ============================================================
# LOGIN LOCATION
# ============================================================

ZAMBIAN_LOCATIONS = [

    "Lusaka",
    "Kitwe",
    "Ndola",
    "Livingstone",
    "Kabwe",
    "Chipata",
    "Chingola",
    "Mufulira",
    "Solwezi",
    "Mazabuka",
    "Kasama",
    "Mongu",
    "Mansa",
    "Luanshya",
    "Choma",
    "Petauke",
    "Kapiri Mposhi",
    "Mkushi",
    "Mpika",
    "Kafue"
]


def choose_login_location(ip_country):

    if ip_country == "Zambia":

        return random.choice(
            ZAMBIAN_LOCATIONS
        )

    international_locations = {

        "South Africa": [
            "Johannesburg",
            "Pretoria",
            "Cape Town",
            "Durban"
        ],

        "United Kingdom": [
            "London",
            "Birmingham",
            "Manchester"
        ],

        "United States": [
            "New York",
            "Atlanta",
            "Washington"
        ],

        "Zimbabwe": [
            "Harare",
            "Bulawayo"
        ],

        "Botswana": [
            "Gaborone",
            "Francistown"
        ],

        "Malawi": [
            "Lilongwe",
            "Blantyre"
        ],

        "Tanzania": [
            "Dar es Salaam",
            "Arusha"
        ],

        "Kenya": [
            "Nairobi",
            "Mombasa"
        ]
    }

    return random.choice(
        international_locations.get(
            ip_country,
            ["International"]
        )
    )


# ============================================================
# DEVICE ID
# ============================================================

def generate_device_id():

    return generate_id(
        "DEV",
        16
    )


# ============================================================
# TRANSACTION STATUS
# ============================================================

def choose_status(parent_status):

    # Most digital transactions succeed.

    if parent_status == "Failed":

        return random.choice([
            "Failed",
            "Failed",
            "Declined"
        ])

    return random.choices(
        [
            "Successful",
            "Failed",
            "Declined",
            "Pending"
        ],
        weights=[
            96,
            2,
            1,
            1
        ],
        k=1
    )[0]


# ============================================================
# MESSY DATA
# ============================================================

def introduce_missing_data(
    channel,
    device_type,
    operating_system,
    device_id,
    login_location
):

    # Deliberately introduce a small amount of incomplete data.

    if random.random() < 0.015:

        device_id = None

    if random.random() < 0.01:

        operating_system = None

    if random.random() < 0.008:

        login_location = None

    if random.random() < 0.005:

        device_type = None

    return (
        device_type,
        operating_system,
        device_id,
        login_location
    )


# ============================================================
# MAIN GENERATION
# ============================================================

def main():

    print("=" * 70)
    print("KWACHA BANK")
    print("SYNTHETIC DIGITAL TRANSACTION DATA GENERATOR")
    print("=" * 70)

    print(f"\nRandom seed: {RANDOM_SEED}")
    print(
        f"Digital transaction rate: "
        f"{DIGITAL_RATE * 100:.0f}%"
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

    try:

        # ====================================================
        # LOAD TRANSACTIONS
        # ====================================================

        print("\nLoading transactions...")

        cursor.execute("""
            SELECT
                transaction_id,
                customer_id,
                transaction_date,
                transaction_type,
                amount,
                channel,
                transaction_status
            FROM transactions
            WHERE transaction_id IS NOT NULL
        """)

        transactions = cursor.fetchall()

        print(
            f"Loaded {len(transactions):,} transactions."
        )

        if not transactions:

            print(
                "\nNo transactions found."
            )

            return

        # ====================================================
        # SELECT DIGITAL TRANSACTIONS
        # ====================================================

        print("\n")
        print("=" * 70)
        print("SELECTING DIGITAL TRANSACTIONS")
        print("=" * 70)

        eligible_transactions = []

        for transaction in transactions:

            original_channel = (
                transaction["channel"]
                or ""
            ).lower()

            # Branch cash and ATM transactions should
            # generally not become digital transactions.

            if original_channel in [
                "branch",
                "branch cash",
                "atm"
            ]:

                continue

            if random.random() <= DIGITAL_RATE:

                eligible_transactions.append(
                    transaction
                )

        print(
            f"\nDigital transactions selected: "
            f"{len(eligible_transactions):,}"
        )

        # ====================================================
        # GENERATE
        # ====================================================

        print("\n")
        print("=" * 70)
        print("GENERATING DIGITAL TRANSACTIONS")
        print("=" * 70)

        generated = []

        channel_counts = {}
        status_counts = {}

        missing_device = 0
        missing_os = 0
        missing_location = 0

        for index, transaction in enumerate(
            eligible_transactions,
            start=1
        ):

            channel = choose_digital_channel(
                transaction
            )

            device_type = choose_device_type(
                channel
            )

            operating_system = (
                choose_operating_system(
                    device_type
                )
            )

            ip_country = choose_ip_country()

            login_location = choose_login_location(
                ip_country
            )

            device_id = generate_device_id()

            status = choose_status(
                transaction["transaction_status"]
            )

            (
                device_type,
                operating_system,
                device_id,
                login_location
            ) = introduce_missing_data(

                channel,
                device_type,
                operating_system,
                device_id,
                login_location
            )

            if device_type is None:
                missing_device += 1

            if operating_system is None:
                missing_os += 1

            if login_location is None:
                missing_location += 1

            row = (

                generate_id(
                    "DIG",
                    14
                ),

                transaction["transaction_id"],

                transaction["customer_id"],

                channel,

                device_type,

                operating_system,

                ip_country,

                login_location,

                transaction["transaction_type"],

                transaction["amount"],

                transaction["transaction_date"],

                device_id,

                status
            )

            generated.append(row)

            channel_counts[channel] = (
                channel_counts.get(
                    channel,
                    0
                ) + 1
            )

            status_counts[status] = (
                status_counts.get(
                    status,
                    0
                ) + 1
            )

            if index % 5000 == 0:

                print(
                    f"  Generated "
                    f"{index:,} / "
                    f"{len(eligible_transactions):,}"
                )

        print(
            "\nGeneration completed."
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("LOCAL GENERATION VALIDATION")
        print("=" * 70)

        print(
            f"\nDigital transactions generated: "
            f"{len(generated):,}"
        )

        print("\nDigital channels:")

        for channel, count in sorted(
            channel_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            percentage = (
                count /
                len(generated) *
                100
            )

            print(
                f"  {channel:<22}"
                f"{count:>7,}"
                f" ({percentage:5.2f}%)"
            )

        print("\nTransaction status:")

        for status, count in sorted(
            status_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            percentage = (
                count /
                len(generated) *
                100
            )

            print(
                f"  {status:<15}"
                f"{count:>7,}"
                f" ({percentage:5.2f}%)"
            )

        print("\nMissing values:")

        print(
            f"  device_type: "
            f"{missing_device:,}"
        )

        print(
            f"  operating_system: "
            f"{missing_os:,}"
        )

        print(
            f"  login_location: "
            f"{missing_location:,}"
        )

        # ====================================================
        # INSERT
        # ====================================================

        print("\n")
        print("=" * 70)
        print("INSERTING INTO MYSQL")
        print("=" * 70)

        insert_sql = """

            INSERT INTO digital_transactions (

                digital_transaction_id,
                transaction_id,
                customer_id,
                channel,
                device_type,
                operating_system,
                ip_country,
                login_location,
                transaction_type,
                amount,
                transaction_datetime,
                device_id,
                status

            )

            VALUES (

                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s

            )

        """

        batch_size = 1000

        for start in range(
            0,
            len(generated),
            batch_size
        ):

            batch = generated[
                start:start + batch_size
            ]

            cursor.executemany(
                insert_sql,
                batch
            )

            connection.commit()

            inserted = min(
                start + batch_size,
                len(generated)
            )

            print(
                f"  {inserted:,} / "
                f"{len(generated):,}"
                f" ({inserted / len(generated) * 100:6.2f}%)"
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
            FROM digital_transactions
        """)

        count = cursor.fetchone()["COUNT(*)"]

        print(
            f"\nDigital transactions currently "
            f"in database: {count:,}"
        )

        cursor.execute("""
            SELECT
                d.digital_transaction_id,
                d.transaction_id,
                d.customer_id,
                CONCAT(
                    c.first_name,
                    ' ',
                    c.last_name
                ) AS customer_name,
                d.channel,
                d.device_type,
                d.operating_system,
                d.ip_country,
                d.login_location,
                d.transaction_type,
                d.amount,
                d.status
            FROM digital_transactions d

            JOIN customers c
                ON d.customer_id = c.customer_id

            ORDER BY RAND()

            LIMIT 10
        """)

        samples = cursor.fetchall()

        print("\nSample digital transactions:\n")

        for row in samples:

            print(
                f"{row['digital_transaction_id']} | "
                f"{row['transaction_id']} | "
                f"{row['customer_name']} | "
                f"{row['channel']} | "
                f"{row['device_type']} | "
                f"{row['operating_system']} | "
                f"{row['ip_country']} | "
                f"K{row['amount']:,.2f} | "
                f"{row['status']}"
            )

        print(
            "\n✓ Digital transaction table "
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
        "KWACHA BANK DIGITAL TRANSACTION "
        "GENERATION FINISHED"
    )
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()