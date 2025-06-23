# 💍 Wedding Budget Planner

The **Wedding Budget Planner** is a comprehensive, user-focused system built to simplify and streamline the financial planning process for weddings. Weddings often involve a variety of expenses that can quickly escalate and become overwhelming. This planner is designed to provide a centralized and organized solution to track, monitor, and manage all wedding-related expenses efficiently.

---

## 📌 Project Overview

This project uses a **Relational Database Management System (RDBMS)** to ensure structured data management with normalization, integrity, and consistency. Users can input and track expenses such as:

- Venue  
- Catering  
- Attire  
- Decorations  
- Photography  
- Gifts  
- And more...

With this system, users can **allocate budgets**, **track actual spending**, and **analyze financial data** in real-time, all within an intuitive interface.

---

## ✨ Key Features

- **Budget vs Actual Expense Comparison**  
  Monitor overspending or savings across different categories.

- **Vendor and Service Provider Management**  
  Store contact info, service details, and costs for easy access.

- **Payment Tracking with Due Dates**  
  Keep track of pending payments and deadlines.

- **Category-wise Expense Reporting**  
  View and analyze expenses based on categories.

- **Custom Query Support**  
  Execute user-friendly SQL queries for detailed insights.

---

## 🛠️ Technical Stack

### Backend (Database)

Built using SQL with support for:

- Table creation and relationships (One-to-Many, Many-to-Many)  
- Normalization (1NF, 2NF, 3NF)  
- Constraints (PRIMARY KEY, FOREIGN KEY, CHECK, etc.)  
- Views and Triggers  
- Indexing for performance  
- Transactions for safe updates  

### Frontend

Basic UI using:

- HTML, CSS, JavaScript  
- *(Optionally extendable using Flask for dynamic functionality)*

---

## 🎯 Learning Objectives

This project demonstrates key database management concepts:

- Real-world application of **DBMS**  
- Mastery of **SQL** through DDL, DML, constraints, triggers, and joins  
- Understanding of **data normalization**  
- Insights into **event management systems** and **financial planning**
  
---

## 🧰 Installation Instructions

### 🔧 Prerequisites

Make sure you have the following installed:

* Python 3.x
* MySQL
* Git (optional, for cloning)
* A browser (Chrome, Edge, etc.)

---

### 📁 Project Setup

#### 1. **Clone the Repository**

```bash
git clone https://github.com/your-username/wedding-budget-planner.git
cd wedding-budget-planner
```

Or download the ZIP and extract it.

---

#### 2. **Set Up the MySQL Database**

1. Open **MySQL Workbench**, **phpMyAdmin**, or your terminal.

2. Create a new database:

   ```sql
   CREATE DATABASE wedding_budget;
   ```

3. Import the database schema:

   ```sql
   USE wedding_budget;
   SOURCE path/to/wedding_budget.sql;
   ```

> Replace `path/to/wedding_budget.sql` with the actual path to your SQL file in the project.

---

#### 3. **Configure Flask App**

Open the `app.py` (or `config.py`) file and update your **MySQL connection settings**:

```python
db = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="wedding_budget"
)
```

> Replace `your_username` and `your_password` with your local MySQL credentials.

---

#### 4. **Install Python Dependencies**

Make sure you’re in your project directory, then install required packages:

```bash
pip install flask mysql-connector-python
```

(Optional: If using a `requirements.txt`, you can run `pip install -r requirements.txt`)

---

#### 5. **Run the Flask App**

```bash
python app.py
```

If everything is set correctly, your Flask server will start, and you can open your browser and go to:

```
http://127.0.0.1:5000
```

---

### ✅ Your App is Ready!

You can now:

* Add wedding budget categories and expenses
* Track vendors and payments
* View reports and budget comparisons

---

### ⚠️ Troubleshooting

* **MySQL connection error?**
  Double-check the host, username, and password in `app.py`.

* **Module not found?**
  Use `pip install <module>` to install missing packages.

* **Flask not running?**
  Ensure you're in the correct folder and using Python 3.

---

### 💌 Final Words
Weddings are emotional and special — and planning them should be stress-free. With the Wedding Budget Planner, financial organization becomes simple, visual, and effective. 🎊
