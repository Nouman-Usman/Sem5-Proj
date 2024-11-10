
from faker import Faker
import random
import csv

fake = Faker()

specializations = [
    "Family Law", "Corporate Law", "Criminal Law", "Constitutional Law", "Tax Law",
    "Civil Law", "Property Law", "Immigration Law", "Labor Law", "Intellectual Property Law",
    "Environmental Law", "Human Rights Law", "Banking Law", "Maritime Law", "Media Law"
]

locations = ["Islamabad", "Lahore", "Karachi", "Peshawar", "Quetta", "Multan", 
             "Faisalabad", "Rawalpindi", "Sialkot", "Gujranwala"]

# Generate 1000 lawyer records
lawyers = []
lawyers.append(["Name", "Specialization", "Experience", "Location", "Rating", "Contact"])

for _ in range(1000):
    name = f"Adv. {fake.name()}"
    specialization = random.choice(specializations)
    experience = f"{random.randint(5, 35)} years"
    location = random.choice(locations)
    rating = round(random.uniform(4.0, 5.0), 1)
    contact = f"+92-{random.randint(300, 349)}-{random.randint(1000000, 9999999)}"
    
    lawyers.append([name, specialization, experience, location, rating, contact])

# Write to CSV file
with open('lawyers.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(lawyers)