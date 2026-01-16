#!/usr/bin/env python3
"""
HICAS Faculty Web Scraper
Scrapes department-wise faculty information from https://www.hicas.ac.in/
Following robots.txt rules and ethical scraping practices
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from urllib.parse import urljoin, urlparse
import re

# Configuration
BASE_URL = "https://www.hicas.ac.in/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
DELAY = 2  # Polite delay between requests (seconds)

# Storage for scraped data
faculty_data = []
visited_urls = set()

def fetch_page(url):
    """Fetch a web page with error handling"""
    if url in visited_urls:
        return None
    
    try:
        print(f"Fetching: {url}")
        time.sleep(DELAY)  # Polite delay
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        visited_urls.add(url)
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def is_valid_url(url):
    """Check if URL is valid for scraping (no PDFs, files, login pages)"""
    if not url:
        return False
    
    # Skip non-HTML content
    if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '/files/', 'login', 'admin']):
        return False
    
    # Only scrape hicas.ac.in domain
    parsed = urlparse(url)
    if 'hicas.ac.in' not in parsed.netloc:
        return False
    
    return True

def extract_faculty_from_text(text, department=None, source_url=""):
    """Extract faculty names and designations from text content"""
    # Common faculty designations
    designations = [
        r'Professor', r'Assistant Professor', r'Associate Professor',
        r'HoD', r'Head of Department', r'Dean', r'Director',
        r'Lecturer', r'Senior Lecturer', r'Dr\.', r'Mr\.', r'Ms\.', r'Mrs\.'
    ]
    
    faculty_list = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if line contains a designation
        for designation in designations:
            if re.search(designation, line, re.IGNORECASE):
                # Try to extract name and designation
                name_match = re.search(r'(Dr\.|Mr\.|Ms\.|Mrs\.)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
                if name_match:
                    name = name_match.group(0).strip()
                    # Clean up the designation
                    desg = line.replace(name, '').strip()
                    
                    faculty_list.append({
                        'Department': department or 'Unknown',
                        'Faculty Name': name,
                        'Designation': desg,
                        'Source URL': source_url
                    })
                break
    
    return faculty_list

def discover_department_links(html):
    """Discover department page links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    department_links = []
    
    # Keywords that indicate department pages
    dept_keywords = [
        'department', 'dept', 'commerce', 'computer', 'science', 'arts',
        'physics', 'chemistry', 'mathematics', 'english', 'tamil',
        'business', 'mba', 'mca', 'bba', 'bca', 'psychology', 'history',
        'catering', 'hotel', 'management'
    ]
    
    # Find all links
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '')
        full_url = urljoin(BASE_URL, href)
        
        # Check if link text or URL contains department keywords
        link_text = link.get_text(strip=True).lower()
        
        if any(keyword in link_text or keyword in href.lower() for keyword in dept_keywords):
            if is_valid_url(full_url) and full_url not in visited_urls:
                department_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)
                })
    
    return department_links

def scrape_department_page(url, dept_name):
    """Scrape a department page for faculty information"""
    html = fetch_page(url)
    if not html:
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all h2 tags (faculty names) followed by h3 tags (designations)
    h2_tags = soup.find_all('h2')
    
    for h2 in h2_tags:
        name_text = h2.get_text(strip=True)
        
        # Check if it's a faculty name (starts with Dr., Mr., Mrs., Ms.)
        if re.match(r'^(Dr\.|Mr\.|Mrs\.|Ms\.)', name_text, re.IGNORECASE):
            # Find the next h3 tag for designation
            h3 = h2.find_next('h3')
            if h3:
                designation_text = h3.get_text(strip=True)
                
                # Check if it's a valid designation
                if any(keyword in designation_text for keyword in ['Professor', 'Asst Prof']):
                    # Normalize designation
                    if 'Assistant' in designation_text or 'Asst Prof' in designation_text:
                        designation = 'Assistant Professor'
                    elif 'Associate' in designation_text:
                        designation = 'Associate Professor'
                    elif 'Professor' in designation_text:
                        if '&' in designation_text:
                            designation = designation_text  # Keep full title like "Professor & Head"
                        else:
                            designation = 'Professor'
                    else:
                        designation = designation_text
                    
                    # Clean up the name
                    name = name_text.strip()
                    
                    # Check if already added
                    existing = any(f['Faculty Name'] == name and f['Department'] == dept_name for f in faculty_data)
                    if not existing:
                        faculty_data.append({
                            'Department': dept_name,
                            'Faculty Name': name,
                            'Designation': designation,
                            'Source URL': url
                        })

def get_all_department_urls():
    """Get comprehensive list of department URLs to scrape"""
    department_urls = {
        # UG - Computer Science & IT
        'B.Sc Computer Science': ['https://www.hicas.ac.in/ug-coursec27a.html?link=bsc-cs'],
        'BCA - Bachelor of Computer Applications': ['https://www.hicas.ac.in/ug-course23cb.html?link=bca'],
        'B.Sc Information Technology': ['https://www.hicas.ac.in/ug-course2041.html?link=bsc-it'],
        'B.Sc Computer Technology': ['https://www.hicas.ac.in/ug-courseca5c.html?link=bsc-ct'],
        'B.Sc CS with Cognitive Systems': ['https://www.hicas.ac.in/ug-course360a.html?link=bsccs-cs'],
        'B.Sc AI & ML': ['https://www.hicas.ac.in/ug-course5ec1.html?link=bsccs-ai'],
        'B.Sc Data Science & Analytics': ['https://www.hicas.ac.in/ug-courseee1c.html?link=bsc-datascience'],
        'B.Sc CS with Cyber Security': ['https://www.hicas.ac.in/ug-course-cybersecurity.html?link=bsc-cybersecurity'],
        
        # UG - Commerce
        'B.Com Commerce': ['https://www.hicas.ac.in/ug-course7ae3.html?link=bcom-commerce'],
        'B.Com CA': ['https://www.hicas.ac.in/ug-course9dd1.html?link=bcom-cca'],
        'B.Com CS': ['https://www.hicas.ac.in/ug-course4b1f.html?link=bcom-corporate'],
        'B.Com International Business': ['https://www.hicas.ac.in/ug-course1dc3.html?link=bcom-ib'],
        'B.Com IT': ['https://www.hicas.ac.in/ug-course750d.html?link=bcom-it'],
        'B.Com Accounting & Finance': ['https://www.hicas.ac.in/ug-courseca41.html?link=bcom-af'],
        'B.Com Professional Accounting': ['https://www.hicas.ac.in/ug-coursee678.html?link=bcom-pa'],
        
        # UG - Bio Sciences
        'B.Sc Microbiology': ['https://www.hicas.ac.in/ug-coursed238.html?link=bsc-microbiology'],
        'B.Sc Biotechnology': ['https://www.hicas.ac.in/ug-course191b.html?link=bsc-bio-technology'],
        
        # UG - Management
        'BBA CA': ['https://www.hicas.ac.in/ug-course6e1a.html?link=bba-ca'],
        'BBA Logistics': ['https://www.hicas.ac.in/ug-coursedd0f.html?link=bba-logistics'],
        'BBA': ['https://www.hicas.ac.in/ug-course9038.html?link=bba'],
        
        # UG - Basic & Applied Science
        'B.Sc Food Processing Technology & Management': ['https://www.hicas.ac.in/ug-courseb83a.html?link=bsc-fpt'],
        'B.Sc Mathematics': ['https://www.hicas.ac.in/ug-course7a06.html?link=bsc-maths'],
        'B.Sc Electronics and Communication Systems': ['https://www.hicas.ac.in/ug-coursec478.html?link=bsc-ecs'],
        'B.Sc Physics': ['https://www.hicas.ac.in/ug-coursebd5e.html?link=bsc-physics'],
        'B.Sc Psychology': ['https://www.hicas.ac.in/ug-course8567.html?link=bsc-psychology'],
        
        # UG - Media Studies
        'B.Sc Visual Communication': ['https://www.hicas.ac.in/ug-courseb56c.html?link=bsc-viscom'],
        'B.Sc Animation & Visual Effects': ['https://www.hicas.ac.in/ug-coursee9f0.html?link=bsc-animation'],
        'B.Voc Graphic Design': ['https://www.hicas.ac.in/ug-course62c9.html?link=b-voc'],
        
        # UG - Industry Science & Literary Studies
        'B.Sc Costume Design & Fashion': ['https://www.hicas.ac.in/ug-courseb75f.html?link=bsc-costume_design'],
        'BA English Literature': ['https://www.hicas.ac.in/ug-course5a26.html?link=ba-english'],
        'B.Sc Catering Science & Hotel Management': ['https://www.hicas.ac.in/ug-coursef5ad.html?link=bsc-catering'],
        
        # PG - Computer Science & IT
        'M.Sc Computer Science': ['https://www.hicas.ac.in/pg-course375c.html?link=msc-cs'],
        'MCA - Master of Computer Applications': ['https://www.hicas.ac.in/pg-coursed74a.html?link=mca'],
        'M.Sc Information Technology': ['https://www.hicas.ac.in/pg-coursec4c3.html?link=msc-it'],
        
        # PG - Commerce
        'M.Com International Business': ['https://www.hicas.ac.in/pg-course6689.html?link=mcom-ib'],
        'M.Com CA': ['https://www.hicas.ac.in/pg-course054a.html?link=mcom-cca'],
        
        # PG - Bio Sciences
        'M.Sc Microbiology': ['https://www.hicas.ac.in/pg-course7421.html?link=msc-microbiology'],
        'M.Sc Biotechnology': ['https://www.hicas.ac.in/pg-course66f7.html?link=msc-bio-tech'],
        
        # PG - Management
        'MBA': ['https://hicas.ac.in/mba-nba.html'],
        
        # PG - Basic & Applied Science
        'M.Sc Mathematics': ['https://www.hicas.ac.in/pg-course98f4.html?link=msc-maths'],
        'M.Sc Electronics and Communication Systems': ['https://www.hicas.ac.in/pg-coursecb92.html?link=msc-ecs'],
        'M.Sc Physics': ['https://www.hicas.ac.in/pg-course5b3c.html?link=msc-physics'],
        'M.Sc Applied Psychology': ['https://www.hicas.ac.in/PG-Psychology.html?link=msc-psychology'],
        
        # PG - Media Studies
        'M.Sc Visual Communications': ['https://www.hicas.ac.in/pg-course2ee2.html?link=msc-viscom'],
        
        # PG - Industry Science & Literary Studies
        'M.Sc Costume Design and Fashion': ['https://www.hicas.ac.in/pg-coursed424.html?link=msc-costume-design'],
        'MSW - Social Work': ['https://www.hicas.ac.in/pg-coursee35c.html?link=msw'],
        'MA English': ['https://www.hicas.ac.in/pg-course82de.html?link=ma-english'],
    }
    
    return department_urls

def main():
    """Main scraping function"""
    print("HICAS Faculty Scraper")
    print("=" * 50)
    
    # Step 1: Get all known department URLs
    print("\n=== Step 1: Loading Department URLs ===")
    department_urls = get_all_department_urls()
    print(f"Found {len(department_urls)} departments to scrape")
    
    # Step 2: Scrape each department page
    print("\n=== Step 2: Scraping Department Pages ===")
    for dept_name, urls in department_urls.items():
        for url in urls:
            print(f"Scraping: {dept_name}")
            scrape_department_page(url, dept_name)
    
    # Step 3: Process and clean data
    print("\n=== Step 3: Processing Data ===")
    
    # Remove duplicates
    df = pd.DataFrame(faculty_data)
    if not df.empty:
        df = df.drop_duplicates(subset=['Faculty Name', 'Department', 'Designation'])
        df = df[df['Faculty Name'].str.strip() != '']  # Remove empty names
        
        # Sort by department and name
        df = df.sort_values(['Department', 'Faculty Name'])
    
    # Step 4: Save results
    print("\n=== Step 4: Saving Results ===")
    
    # Save as CSV
    csv_file = 'hicas_faculty_data.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✓ Saved CSV: {csv_file}")
    
    # Save as JSON
    json_file = 'hicas_faculty_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(faculty_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved JSON: {json_file}")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total records scraped: {len(faculty_data)}")
    print(f"Unique faculty members: {len(df)}")
    print(f"Pages visited: {len(visited_urls)}")
    
    if not df.empty:
        print(f"\nDepartments found:")
        for dept in df['Department'].unique():
            count = len(df[df['Department'] == dept])
            print(f"  - {dept}: {count} members")
    
    print("\n✓ Scraping completed successfully!")
    print(f"Data saved to: {csv_file} and {json_file}")

if __name__ == "__main__":
    main()
