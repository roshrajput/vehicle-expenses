# 🚗 AutoExpense OS — Vehicle Expense & Mileage Tracker

A consumer-grade, modern Streamlit SaaS web application to track vehicle fuel efficiency, service records, and fleet expenses backed by Google Sheets.

## ✨ Features

- **🔐 Consumer-grade Auth & Setup**:
  - Sign in or register accounts stored directly in the `Users` tab of your Google Sheet.
  - Interactive onboarding assistant to upload your Google Cloud service account `.json` key with 1 click.
- **🚗 My Garage (Vehicle Fleet Management)**:
  - Real-time fleet overview: Total fleet spend, vehicle count, and Google Sheets sync status.
  - Spec cards with authentic Indian registration number plates, technical specifications, and lifetime spend per vehicle.
  - Add, edit, and soft-delete vehicles with a confirmation dialog.
- **⛽ Smart Fuel Fill-Up Logging**:
  - Date, Odometer reading, Trip meter, and Litres filled.
  - **Smart Rate / Cost Calculator**: Enter *either* Rate/Litre *or* Total Bill — the other auto-computes!
  - **Full-Tank Flag**: Computes accurate km/l mileage using the consecutive full-tank method.
  - Modern financial transaction stream with quick edit and soft-delete actions.
- **🔧 Service & Maintenance Logging**:
  - Classify repairs (Regular Service, Tyres, Battery, Insurance, Body Work, Electrical).
  - Odometer at service, parts and labour cost breakdown, and workshop notes.
- **📦 Miscellaneous & Tolls**:
  - Log FASTag, expressway tolls, parking tickets, car washes, and fines.
- **📊 Executive Analytics Dashboard**:
  - **8 Live KPI Metric Cards**: Last Month Total (with comparison delta), Current Month Running Total, Real km/L Fuel Mileage, Total Distance Tracked, Running Cost per km (₹/km), Filtered Spend, Average Fill-up Bill, and Next Service Due Schedule.
  - **Interactive Plotly Visualizations**:
    - Monthly Spending Trajectory (Fuel, Service, Misc, and Total line)
    - Category Allocation (Donut chart with custom tooltips)
    - Spend Comparison by Vehicle (Horizontal bar chart)
    - Fuel Price Trajectory over time (₹ / Litre)
  - Date range filters and vehicle filtering.
  - 🔄 One-click Google Sheets cache sync button.
- **🛡️ Soft Delete (No Hard Deletes)**:
  - Deleted entries receive an `is_deleted = "TRUE"` flag, permanently archiving historical data in Google Sheets while hiding them in the UI.

---

## 🛠️ Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Launch App
```powershell
streamlit run app.py
```

### 3. Connect Google Sheet
1. Open your sheet: [vehicle-expense-sheet](https://docs.google.com/spreadsheets/d/1wR0BmHktXMGs1q9_39k7gg86BCdfuPbxuLMSwC6H85A/edit)
2. Share the spreadsheet with your Google Cloud Service Account email as **Editor**.
3. Upload your downloaded `.json` key directly into the app setup assistant (or place it in `.streamlit/secrets.toml`).

---

## 📁 Project Architecture

```
Vehicle Expense/
├── .streamlit/
│   ├── config.toml              # Tailwind-inspired Slate & Azure theme
│   ├── secrets.toml.example     # Service account template
│   └── secrets.toml             # Live credentials (git-ignored)
├── app.py                       # App entry point, router, and Setup Assistant
├── pages/
│   ├── login.py                 # Modern SaaS authentication & registration
│   ├── home.py                  # My Garage fleet management & spec cards
│   ├── expenses.py              # Fuel, Service & Misc transaction logger
│   └── dashboard.py             # Executive KPI metrics & Plotly charts
├── utils/
│   ├── __init__.py
│   ├── ui.py                    # Plus Jakarta Sans design system, badges & cards
│   ├── auth.py                  # User session & registration logic
│   ├── constants.py             # Column headers, dropdown categories, currency (₹)
│   ├── helpers.py               # ID generator, date formatting, currency formatters
│   └── sheets.py                # gspread wrapper, cache control & soft-delete logic
├── requirements.txt
├── .gitignore
└── README.md
```
