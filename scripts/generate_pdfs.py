from fpdf import FPDF
import os
import random
from faker import Faker

fake = Faker()

OUTPUT_DIR = "sample_pdfs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def create_license_pdf(filename, provider_name, npi, license_num):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="STATE MEDICAL BOARD", ln=1, align="C")
    pdf.ln(20)
    
    pdf.set_font("Arial", size=24)
    pdf.cell(200, 10, txt="MEDICAL LICENSE", ln=1, align="C")
    pdf.ln(20)
    
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"This certifies that {provider_name}", ln=1, align="C")
    pdf.cell(200, 10, txt="is duly licensed to practice medicine.", ln=1, align="C")
    pdf.ln(10)
    
    pdf.cell(200, 10, txt=f"License Number: {license_num}", ln=1, align="L")
    pdf.cell(200, 10, txt=f"NPI: {npi}", ln=1, align="L")
    pdf.cell(200, 10, txt=f"Expiration Date: {fake.future_date()}", ln=1, align="L")
    
    pdf.output(os.path.join(OUTPUT_DIR, filename))

def generate_sample_pdfs(count=10):
    print(f"Generating {count} sample PDFs...")
    # Generate some Dummy PDFs
    for i in range(count):
        name = fake.name()
        npi = str(fake.random_number(digits=10, fix_len=True))
        license_num = f"LIC-{fake.random_number(digits=6)}"
        filename = f"license_{npi}.pdf"
        create_license_pdf(filename, name, npi, license_num)
    print(f"Generated {count} PDFs in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_sample_pdfs()
