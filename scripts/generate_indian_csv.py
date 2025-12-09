import pandas as pd
import random
import string

# Generate synthetic Indian provider dataset
num_rows = 50
states = ["TN", "MH", "DL", "KA", "KL", "GJ", "RJ", "UP", "WB", "AP"]
specializations = ["General Physician", "Cardiologist", "Dermatologist"]
cities = ["Chennai", "Mumbai", "Delhi"]

def random_reg_number():
    st = random.choice(states)
    number = "".join(random.choices(string.digits, k=5))
    return f"{st}MC/{number}"

data = []
for i in range(1, num_rows + 1):
    data.append({
        "provider_id": i,
        "full_name": f"Dr. ValidTest {i}",
        "registration_number": random_reg_number(),  # This should be detected
        "specialization": random.choice(specializations),
        "city": random.choice(cities)
    })

df = pd.DataFrame(data)
df.to_csv("indian_providers.csv", index=False)
print("Created indian_providers.csv")
