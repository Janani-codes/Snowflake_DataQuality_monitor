# Snowflake Data Quality Monitor

## Project Overview

This project is an end-to-end Data Quality Monitoring System built using Python, Snowflake, SQL and Streamlit.

The application loads CSV data into Snowflake, performs automated Data Quality checks, stores the results, and displays them using an interactive dashboard.

---

## Technologies Used

- Python
- Snowflake
- SQL
- Streamlit
- Pandas
- Plotly

---

## Project Structure

```
Snowflake-DQ-Monitor/

│── app.py
│── config.py
│── load_data.py
│── dq_checks.py
│── scheduler.py
│── requirements.txt
│── README.md
│── .env
```

---

## Features

- Load CSV into Snowflake
- Null Check
- Duplicate Check
- Range Check
- Freshness Check
- Health Score Dashboard
- Interactive Charts
- CSV Download
- Scheduler

---

## Installation

### Clone Repository

```
git clone <repository-url>
```

---

### Install Dependencies

```
py -m pip install -r requirements.txt
```

---

### Configure .env

Create a file named `.env`

```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=DQ_MONITOR_DB
SNOWFLAKE_SCHEMA=DQ_SCHEMA
```

---

## Run the Project

### Step 1

```
py load_data.py
```

Loads the CSV into Snowflake.

---

### Step 2

```
py dq_checks.py
```

Runs Data Quality checks.

---

### Step 3

```
py -m streamlit run app.py
```

Starts the dashboard.

---

## Data Quality Checks

- Null Check
- Duplicate Check
- Range Check
- Freshness Check

---

## Workflow

```
CSV Dataset
      │
      ▼
load_data.py
      │
      ▼
Snowflake
      │
      ▼
dq_checks.py
      │
      ▼
DQ_RESULTS
      │
      ▼
Streamlit Dashboard
```

---

## Future Enhancements

- Support multiple datasets
- Email Alerts
- Slack Notifications
- Great Expectations Integration

---

## Author

Janani 