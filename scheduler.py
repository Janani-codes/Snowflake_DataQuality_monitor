import time
import subprocess
import sys

# Run every 1 hour
INTERVAL = 3600

print("🚀 Snowflake Data Quality Scheduler Started...")

while True:
    print("\n========================================")
    print("▶ Running Data Quality Checks...")

    # Run dq_checks.py using the current Python interpreter
    subprocess.run([sys.executable, "dq_checks.py"])

    print("✅ Checks completed successfully.")
    print(f"⏳ Waiting {INTERVAL} seconds for next run...")
    print("========================================")

    time.sleep(INTERVAL)