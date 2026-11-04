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

## What's New in Version 2.0

## Dashboard Preview

The Snowflake Data Quality Monitor provides an interactive dashboard to monitor data quality, analyze failures, and track overall data health.

![Streamlit Dashboard](screenshots/Streamlit%20Dashboard.png)


* **Enhanced Dashboard UI:** Improved Streamlit dashboard with a cleaner and more professional interface.
* **Interactive Visualizations:** Added interactive Plotly charts for better data analysis.
* **Data Health Monitoring:** Monitor overall data quality using health scores and KPI cards.
* **Historical Failure Trends:** Visualize data quality failures over time.
* **Demo Mode:** Explore the dashboard using sample data without requiring an active Snowflake connection.

### Running in Demo Mode

The dashboard supports a demo mode that uses sample data. This allows users to explore its features without connecting to Snowflake.

Set `DEMO_MODE = True` in `app.py` to enable demo mode.


## Future Enhancements

- Support multiple datasets
- Email Alerts
- Slack Notifications
- Great Expectations Integration

---

## Author

Janani 
