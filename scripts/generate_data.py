import random
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import Provider, VerificationStatus

# Ensure tables exist
Base.metadata.create_all(bind=engine)

fake = Faker()

SPECIALTIES = [
    "Cardiology", "Dermatology", "Family Medicine", "Internal Medicine", 
    "Neurology", "Pediatrics", "Psychiatry", "Surgery", "Orthopedics"
]

def generate_providers(n=200):
    db: Session = SessionLocal()
    print(f"Generating {n} synthetic providers...")
    
    for _ in range(n):
        # Generate NPI (10 digits)
        npi = str(fake.random_number(digits=10, fix_len=True))
        
        provider = Provider(
            npi=npi,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            specialty=random.choice(SPECIALTIES),
            address_line1=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            zip_code=fake.zipcode(),
            phone=fake.phone_number(),
            email=fake.email(),
            website_url=fake.url(),
            status=VerificationStatus.REVIEW,
            overall_confidence_score=0.0
        )
        db.add(provider)
    
    try:
        db.commit()
        print("Successfully generated data.")
    except Exception as e:
        print(f"Error generating data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_providers()
