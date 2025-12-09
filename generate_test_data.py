import csv
import random

# Constants
SPECIALTIES = ['Cardiologist', 'Dermatologist', 'General Physician', 'Neurologist', 'Pediatrician', 'Orthopedic Surgeon']
CITIES_IN = ['Chennai', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad']
CITIES_US = ['New York', 'Chicago', 'Los Angeles', 'Houston', 'Phoenix']
FIRST_NAMES = ['Rajesh', 'Priya', 'Amit', 'Suresh', 'Deepa', 'John', 'Alice', 'Robert', 'Emily', 'Michael']
LAST_NAMES = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
STATES = ['TNMC', 'UPMC', 'MHMC', 'DLMC', 'KA']

def generate_indian_reg():
    state = random.choice(STATES)
    number = random.randint(10000, 99999)
    return f"{state}/{number}"

def generate_us_npi():
    return str(random.randint(1000000000, 9999999999))

rows = []
# Header
rows.append(['provider_id', 'full_name', 'registration_number', 'specialization', 'city', 'npi', 'website'])

for i in range(1, 301):
    is_indian = random.choice([True, True, False]) # Bias towards Indian for this user
    
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    full_name = f"Dr. {fname} {lname}"
    
    specialty = random.choice(SPECIALTIES)
    
    if is_indian:
        city = random.choice(CITIES_IN)
        reg_no = generate_indian_reg()
        npi = ""
        website = f"https://{fname.lower()}{lname.lower()}.in"
    else:
        city = random.choice(CITIES_US)
        reg_no = ""
        npi = generate_us_npi()
        website = f"https://{fname.lower()}{lname.lower()}.com"
        
    # Inject some errors (10% chance)
    if random.random() < 0.1:
        if is_indian:
            reg_no = "INVALID-ID"
        else:
            npi = "123" # too short

    rows.append([i, full_name, reg_no, specialty, city, npi, website])

with open('large_test_providers.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Generated {len(rows)-1} records in large_test_providers.csv")
