#!/usr/bin/env python3
"""
Generate simulated student data for HICAS departments.
Creates hicas_students_simulated.csv with 40 students per year:
- UG: 3 years (1-3) => 120 students per UG department
- PG: 2 years (1-2) => 80 students per PG department
Names are sampled from a curated Indian names list.
"""

import csv
import random
from pathlib import Path
from datetime import datetime

# Fixed seed for reproducibility
random.seed(42)

# Department source (mirrors scrape_hicas_faculty.py)
UG_DEPARTMENTS = [
    'B.Sc Computer Science',
    'BCA - Bachelor of Computer Applications',
    'B.Sc Information Technology',
    'B.Sc Computer Technology',
    'B.Sc CS with Cognitive Systems',
    'B.Sc AI & ML',
    'B.Sc Data Science & Analytics',
    'B.Sc CS with Cyber Security',
    'B.Com Commerce',
    'B.Com CA',
    'B.Com CS',
    'B.Com International Business',
    'B.Com IT',
    'B.Com Accounting & Finance',
    'B.Com Professional Accounting',
    'B.Sc Microbiology',
    'B.Sc Biotechnology',
    'BBA CA',
    'BBA Logistics',
    'BBA',
    'B.Sc Food Processing Technology & Management',
    'B.Sc Mathematics',
    'B.Sc Electronics and Communication Systems',
    'B.Sc Physics',
    'B.Sc Psychology',
    'B.Sc Visual Communication',
    'B.Sc Animation & Visual Effects',
    'B.Voc Graphic Design',
    'B.Sc Costume Design & Fashion',
    'BA English Literature',
    'B.Sc Catering Science & Hotel Management',
]

PG_DEPARTMENTS = [
    'M.Sc Computer Science',
    'MCA - Master of Computer Applications',
    'M.Sc Information Technology',
    'M.Com International Business',
    'M.Com CA',
    'M.Sc Microbiology',
    'M.Sc Biotechnology',
    'MBA',
    'M.Sc Mathematics',
    'M.Sc Electronics and Communication Systems',
    'M.Sc Physics',
    'M.Sc Applied Psychology',
    'M.Sc Visual Communications',
    'M.Sc Costume Design and Fashion',
    'MSW - Social Work',
    'MA English',
]

# Name pools
MALE_NAMES = [
    'Aarav','Vivaan','Aditya','Vihaan','Arjun','Reyansh','Mohammed','Sai','Ishaan','Shaurya',
    'Atharv','Dhruv','Kabir','Ritvik','Rohan','Karthik','Sanjay','Nikhil','Rakesh','Pranav',
    'Abhinav','Harsh','Yash','Rajat','Sameer','Siddharth','Ayaan','Manav','Krishna','Vikram'
]
FEMALE_NAMES = [
    'Aadhya','Anaya','Diya','Jiya','Myra','Sara','Anika','Ira','Meera','Advika',
    'Navya','Pari','Riya','Saanvi','Ishita','Prisha','Aarohi','Vaishnavi','Anjali','Shruti',
    'Sneha','Nandini','Bhavya','Aditi','Harini','Keerthi','Lavanya','Pooja','Tara','Divya'
]
LAST_NAMES = [
    'Sharma','Iyer','Nair','Reddy','Kumar','Singh','Patel','Gupta','Das','Menon',
    'Rao','Chopra','Kapoor','Mehta','Bose','Dutta','Jain','Verma','Yadav','Shetty',
    'Mishra','Chaudhary','Gowda','Kulkarni','Pillai','Mukherjee','Banerjee','Bhatt','Pandey','Shukla'
]

def make_name():
    first = random.choice(MALE_NAMES + FEMALE_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


def build_department_codes():
    """Assign a unique 3-digit code per department starting at 301."""
    all_depts = UG_DEPARTMENTS + PG_DEPARTMENTS
    base = 301
    return {dept: f"{base + idx}" for idx, dept in enumerate(all_depts)}


def build_students():
    rows = []
    dept_codes = build_department_codes()
    college_code = "8230"
    current_year_two_digit = int(str(datetime.now().year)[-2:])
    serial_tracker = {}

    # UG: 3 years, 40 students per year
    for dept in UG_DEPARTMENTS:
        for year in (1, 2, 3):
            serial_tracker[(dept, year)] = 0
            for _ in range(40):
                serial_tracker[(dept, year)] += 1
                serial = serial_tracker[(dept, year)]
                batch_year = (current_year_two_digit - year + 1) % 100  # e.g., Y1->26, Y2->25
                reg = f"{college_code}{batch_year:02d}{dept_codes[dept]}{serial:02d}"
                rows.append({
                    'Department': dept,
                    'ProgramLevel': 'UG',
                    'Year': year,
                    'BatchYear': f"{batch_year:02d}",
                    'RegisterNumber': reg,
                    'Student Name': make_name(),
                    'Email': f"{reg}@hicas.ac.in",
                })

    # PG: 2 years, 40 students per year
    for dept in PG_DEPARTMENTS:
        for year in (1, 2):
            serial_tracker[(dept, year)] = 0
            for _ in range(40):
                serial_tracker[(dept, year)] += 1
                serial = serial_tracker[(dept, year)]
                batch_year = (current_year_two_digit - year + 1) % 100  # e.g., Y1->26, Y2->25
                reg = f"{college_code}{batch_year:02d}{dept_codes[dept]}{serial:02d}"
                rows.append({
                    'Department': dept,
                    'ProgramLevel': 'PG',
                    'Year': year,
                    'BatchYear': f"{batch_year:02d}",
                    'RegisterNumber': reg,
                    'Student Name': make_name(),
                    'Email': f"{reg}@hicas.ac.in",
                })

    return rows


def main():
    rows = build_students()
    out_path = Path('hicas_students_simulated.csv')
    with out_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'Department', 'ProgramLevel', 'Year', 'BatchYear',
                'RegisterNumber', 'Student Name', 'Email'
            ]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {out_path} with {len(rows)} simulated students.")


if __name__ == '__main__':
    main()
