# PostgreSQL Setup Instructions

## Step 1: Set Your PostgreSQL Password

Open the file: `smartintern/settings.py`

Find this line:
```python
'PASSWORD': 'your_password',  # Change this to your PostgreSQL password
```

Replace `'your_password'` with the password you set during PostgreSQL installation.

## Step 2: Create Database

Open **pgAdmin 4** or **SQL Shell (psql)** and run:

```sql
CREATE DATABASE smartintern_db;
```

**OR** use command line (easier):

```bash
# In PowerShell, run:
cd "C:\Program Files\PostgreSQL\15\bin"
.\psql -U postgres

# Then in psql:
CREATE DATABASE smartintern_db;
\q
```

## Step 3: Run Migrations

After creating database, run:

```bash
python manage.py migrate
```

## Step 4: Load Sample Data

```bash
python manage.py load_sample_data
```

## Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Troubleshooting:

**Error: "password authentication failed"**
- Check the password in settings.py matches PostgreSQL password

**Error: "database does not exist"**
- Run: `CREATE DATABASE smartintern_db;` in PostgreSQL

**Error: "could not connect to server"**
- Make sure PostgreSQL service is running
- Check Windows Services → PostgreSQL 15 → Start

## Connection Details:
- **Database:** smartintern_db
- **User:** postgres
- **Host:** localhost
- **Port:** 5432

## Verify PostgreSQL is Running:

```bash
# In PowerShell:
Get-Service -Name postgresql*
```

Should show "Running" status.