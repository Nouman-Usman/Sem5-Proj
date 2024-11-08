import csv

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
    
    best_lawyer = max(relevant_lawyers, key=lambda l: float(l["Ratings"]))
    return (
        f"Recommended lawyer: {best_lawyer['Lawyer Name']}, Specialty: {best_lawyer['Type (Specialty)']}, "
        f"Experience: {best_lawyer['Experience (Years)']} years, Ratings: {best_lawyer['Ratings']}/5, "
        f"Location: {best_lawyer['Location']}."
    )
