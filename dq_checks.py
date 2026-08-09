import snowflake.connector
from config import SNOWFLAKE_CONFIG
from datetime import datetime


# ---------------------------------------------------
# Create Snowflake Connection
# ---------------------------------------------------
def get_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_CONFIG["account"],
        user=SNOWFLAKE_CONFIG["user"],
        password=SNOWFLAKE_CONFIG["password"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"]
    )


# ---------------------------------------------------
# Log Result into DQ_RESULTS Table
# ---------------------------------------------------
def log_result(cursor, check_name, table_name, column_name,
               status, failed_count, failed_percentage):

    cursor.execute("""
        INSERT INTO DQ_RESULTS
        (
            CHECK_NAME,
            TABLE_NAME,
            COLUMN_NAME,
            STATUS,
            FAILED_COUNT,
            FAILED_PERCENTAGE,
            RUN_TIMESTAMP
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        check_name,
        table_name,
        column_name,
        status,
        failed_count,
        failed_percentage,
        datetime.now()
    ))


# ---------------------------------------------------
# NULL CHECK
# ---------------------------------------------------
def check_nulls():

    conn = get_connection()
    cursor = conn.cursor()

    table = "DIRTY_RAW_ORDERS"
    column = "CUSTOMER_ID"

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM {table}
        WHERE {column} IS NULL
    """)

    failed = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total = cursor.fetchone()[0]

    percentage = (failed / total) * 100
    status = "FAIL" if failed > 0 else "PASS"

    log_result(
        cursor,
        "NULL CHECK",
        table,
        column,
        status,
        failed,
        percentage
    )

    conn.commit()

    print("\n------------------------------")
    print("NULL CHECK")
    print("------------------------------")
    print("Failed Rows :", failed)
    print("Percentage :", round(percentage, 2), "%")
    print("Status :", status)

    cursor.close()
    conn.close()


# ---------------------------------------------------
# DUPLICATE CHECK
# ---------------------------------------------------
def check_duplicates():

    conn = get_connection()
    cursor = conn.cursor()

    table = "DIRTY_RAW_ORDERS"
    column = "ROW_ID"

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM (
            SELECT {column}
            FROM {table}
            GROUP BY {column}
            HAVING COUNT(*) > 1
        )
    """)

    failed = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total = cursor.fetchone()[0]

    percentage = (failed / total) * 100
    status = "FAIL" if failed > 0 else "PASS"

    log_result(
        cursor,
        "DUPLICATE CHECK",
        table,
        column,
        status,
        failed,
        percentage
    )

    conn.commit()

    print("\n------------------------------")
    print("DUPLICATE CHECK")
    print("------------------------------")
    print("Failed Rows :", failed)
    print("Percentage :", round(percentage, 2), "%")
    print("Status :", status)

    cursor.close()
    conn.close()


# ---------------------------------------------------
# RANGE CHECK
# ---------------------------------------------------
def check_range():

    conn = get_connection()
    cursor = conn.cursor()

    table = "DIRTY_RAW_ORDERS"

    checks = [
        ("SALES", "SALES < 0"),
        ("QUANTITY", "QUANTITY <= 0"),
        ("DISCOUNT", "DISCOUNT < 0 OR DISCOUNT > 1")
    ]

    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total = cursor.fetchone()[0]

    for column, condition in checks:

        cursor.execute(f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE {condition}
        """)

        failed = cursor.fetchone()[0]

        percentage = (failed / total) * 100
        status = "FAIL" if failed > 0 else "PASS"

        log_result(
            cursor,
            "RANGE CHECK",
            table,
            column,
            status,
            failed,
            percentage
        )

        print("\n------------------------------")
        print(f"RANGE CHECK ({column})")
        print("------------------------------")
        print("Failed Rows :", failed)
        print("Percentage :", round(percentage, 2), "%")
        print("Status :", status)

    conn.commit()

    cursor.close()
    conn.close()


# ---------------------------------------------------
# FRESHNESS CHECK
# ---------------------------------------------------
def check_freshness():

    conn = get_connection()
    cursor = conn.cursor()

    table = "DIRTY_RAW_ORDERS"

    cursor.execute(f"""
        SELECT MAX(ORDER_DATE)
        FROM {table}
    """)

    latest_date = cursor.fetchone()[0]

    print("\n------------------------------")
    print("FRESHNESS CHECK")
    print("------------------------------")
    print("Latest Order Date :", latest_date)

    cursor.close()
    conn.close()


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
if __name__ == "__main__":

    print("\n========================================")
    print("   SNOWFLAKE DATA QUALITY MONITOR")
    print("========================================")

    check_nulls()
    check_duplicates()
    check_range()
    check_freshness()

    print("\n========================================")
    print(" DATA QUALITY CHECKS COMPLETED")
    print("========================================")