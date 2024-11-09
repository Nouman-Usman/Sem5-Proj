import csv
import random

def calculate_weight(rating, experience):
    # Normalize ratings (assuming 5 is max) and experience (assuming 40 years is max)
    normalized_rating = float(rating) / 5
    normalized_exp = float(experience) / 20
    # Combined weight with 60% emphasis on rating and 40% on experience
    return (0.6 * normalized_rating + 0.4 * normalized_exp)

def recommend_lawyer(category):
    lawyers = []
    with open("lawyers.csv", mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            lawyers.append(row)
    
    relevant_lawyers = [
        lawyer for lawyer in lawyers if lawyer["Type (Specialty)"].lower() == category.lower()
    ]
    
    if not relevant_lawyers:
        return "No lawyer found for this specialty."
    
    # Calculate weights for each relevant lawyer
    weights = [calculate_weight(lawyer["Ratings"], lawyer["Experience (Years)"]) 
              for lawyer in relevant_lawyers]
    selected_lawyer = random.choices(relevant_lawyers, weights=weights, k=2)[0]
    
    return (
        f"Recommended lawyer: {selected_lawyer['Lawyer Name']}, Specialty: {selected_lawyer['Type (Specialty)']}, "
        f"Experience: {selected_lawyer['Experience (Years)']} years, Ratings: {selected_lawyer['Ratings']}/5, "
        f"Location: {selected_lawyer['Location']}."
    )
