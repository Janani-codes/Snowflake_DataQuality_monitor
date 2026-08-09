import snowflake.connector
from config import SNOWFLAKE_CONFIG

try:
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_CONFIG["account"],
        user=SNOWFLAKE_CONFIG["user"],
        password=SNOWFLAKE_CONFIG["password"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"]
    )

    print("✅ Connected to Snowflake")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM RAW_ORDERS
        LIMIT 5
    """)

    rows = cursor.fetchall()

    print("\nFirst 5 Records:\n")

    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print(e)