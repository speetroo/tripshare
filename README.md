# Tripshare – Django Group Expense Splitter

Tripshare is a web application built with **Django** that helps groups of people share expenses fairly.

Think: trips with friends, shared apartments, events, etc.  
You can create groups, add members, define currencies, log expenses, and see **who should pay whom** both per group and globally across all groups.

---

## Features

### 🔐 User Accounts

- User **registration** (create your own account)
- User **login/logout**
- Django admin interface for superusers

### 👥 Groups & Members

- Create **groups** (e.g. “Ibiza Trip”, “Flat 2024”, “Ski Weekend”)
- Add multiple **members** (users) to each group
- Each group is independent (its own expenses & currencies)

### 💱 Currencies

- Each group can have one or more **currencies** (EUR, USD, etc.)
- Each currency has a **rate to EUR**
- All balances, status and clearing are computed in **EUR**

### 💸 Expenses

For each expense you can specify:

- The **group**
- A short **description**
- The **amount**
- The **currency** (one of the group’s currencies)
- **Who paid** (payer)
- **Who benefited** (one or more beneficiaries, via checkboxes)
- **Date** of the expense

The app automatically:

- Converts the expense to EUR using the group’s currency rate
- Splits the amount **equally among beneficiaries**
- Credits the **payer** and debits the **beneficiaries**

### 📊 Per-group Balances & Clearing

For each group:

- Shows **per-user net balance** in EUR:
  - Positive → the user should **receive** money  
  - Negative → the user should **pay** money  
  - Zero → **settled**
- Computes a **settlement plan**:
  - List of “**X should pay Y Z €**”
  - Based on all expenses in the group
  - Uses netting to simplify who pays whom

### 🌍 Global Clearing (Across All Groups)

- Combines balances from **all groups**
- Shows each user’s **global net balance**
- Computes a **global settlement plan**, so:
  - If Alice owes Bob in one group but Bob owes Alice in another, the debts cancel out.
  - You see only the **final minimal transfers**.

### 🙋 My Status

- For the logged-in user:
  - List of groups where they are a member
  - Total amount they **paid** in each group (in EUR)
  - Their **net balance** per group (receive / pay / settled)

### 🎨 UI & Themes

- Clean UI using **Bootstrap** + custom CSS
- Warm light theme
- Optional **dark mode**:
  - Toggle button in the navbar (🌙 / ☀️)
  - Theme preference is stored in `localStorage` and persists across pages

---

## Tech Stack

- **Python** (3.x)
- **Django** (6.x)
- **SQLite** (default Django DB for development)
- **Bootstrap 5** (via CDN)
- Custom CSS for theming (light/dark)

No extra Django apps or external services are required.

---

## Getting Started

These steps are similar for **Windows**, **macOS**, and **Linux**.  
The main difference is the virtual environment / activation commands.

### 1. Clone the repository

```bash
git clone git@github.com:speetroo/tripshare.git
cd tripshare
```

---

### 2. Create a virtual environment

Windows - PowerShell
```bash
python -m venv venv
```

macOS / Linux
```bash
python3 -m venv venv
```

---

### 3. Activate the virtual environment

Windows - PowerShell
```bash
venv\Scripts\Activate.ps1
```

macOS / Linux
```bash
source venv/bin/activate
```
You should see `(venv)` at the beginning of your terminal prompt.

---

### 4. Install dependencies

```bash
pip install django
```

You can verify Django is installed:
```bash
python -m django --version
```

---

### 5. Database setup (migrations)

Initialize the SQLite database:
```bash
python manage.py migrate
```
This creates `db.sqlite3` with all required tables.

---

### 6. Create a superuse (admin)
This lets you log into /admin/ and manage users/groups manually if needed.
```bash
python manage.py createsuperuser
```

---

### 7. Run the development server
```bash
python manage.py runserver
```
Visit:
- Main app: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

---



## Project structure (simplified)
```text
tripshare/
├─ manage.py
├─ config/                 # Django project settings & URLs
│  ├─ settings.py
│  ├─ urls.py
│  ├─ asgi.py / wsgi.py
│
├─ core/                   # Main application
│  ├─ models.py            # Group, Currency, Expense
│  ├─ views.py             # Views for groups, expenses, status, clearing, auth
│  ├─ urls.py              # App URL patterns
│  ├─ forms.py             # Forms for Group, Expense, Currency
│  ├─ admin.py             # Admin registrations
│  └─ static/core/
│     └─ style.css         # Custom CSS (themes)
│
├─ templates/
│  ├─ base.html            # Main layout & navbar
│  ├─ core/
│  │  ├─ group_list.html
│  │  ├─ group_detail.html
│  │  ├─ create_group.html
│  │  ├─ create_expense.html
│  │  ├─ add_currency.html
│  │  ├─ my_status.html
│  │  └─ global_clearing.html
│  └─ registration/
│     ├─ login.html
│     └─ register.html
│
└─ venv/                   # Virtual environment (ignored by git)
```