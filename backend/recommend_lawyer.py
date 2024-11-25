import csv
import heapq

def calculate_weight(rating, experience):
    try:
        normalized_rating = float(rating) / 5
        years = int(experience.split()[0]) 
        normalized_exp = float(years) / 35 
        return (0.6 * normalized_rating + 0.4 * normalized_exp)
    except (ValueError, IndexError) as e:
        print(f"Error calculating weight: {e}")
        return 0

def recommend(category):
    try:
        # Read the CSV file
        with open("lawyers.csv", mode="r", encoding='utf-8') as file:
            lawyers = list(csv.DictReader(file))
            
        if not lawyers:
            print("No lawyers found in database")
            return []

        # Standardize the category mapping
        specialty_mapping = {
            "Civil": "Civil",
            "Criminal": "Criminal",
            "Corporate": "Corporate",
            "Constitutional": "Constitutional",
            "Tax": "Tax",
            "Family": "Family",
            "Intellectual Property": "Intellectual Property",
            "Labor and Employment": "Labor and Employment",
            "Immigration": "Immigration",
            "Human Rights": "Human Rights",
            "Environmental": "Environmental",
            "Banking and Finance": "Banking and Finance",
            "Cyber Law": "Cyber Law",
            "Alternate Dispute Resolution (ADR)": "Alternate Dispute Resolution (ADR)"
        }

        mapped_category = specialty_mapping.get(category, category)
        print(f"Looking for lawyers with specialization: {mapped_category}")

        # Filter and rank lawyers
        relevant_lawyers = []
        for lawyer in lawyers:
            try:
                if lawyer["Specialization"].strip() == mapped_category:
                    weight = calculate_weight(
                        lawyer["Rating"],
                        lawyer["Experience"]
                    )
                    relevant_lawyers.append((lawyer, weight))
            except KeyError as e:
                print(f"Missing field in lawyer data: {e}")
                continue

        if not relevant_lawyers:
            print(f"No lawyers found for category: {mapped_category}")
            return []

        # Get top 2 lawyers based on weights
        top_lawyers = heapq.nlargest(2, relevant_lawyers, key=lambda x: x[1])
        return [lawyer for lawyer, _ in top_lawyers]

    except Exception as e:
        print(f"Error in recommend function: {e}")
        return []

def recommend_lawyer(category):
    """Legacy function that returns formatted string instead of lawyer objects"""
    lawyers = recommend(category)
    if not lawyers:
        return "No lawyers found for this specialty."
    
    recommendation = "Top recommended lawyers:\n\n"
    for lawyer in lawyers:
        recommendation += (
            f"- {lawyer['Name']}\n"
            f"  Specialty: {lawyer['Specialization']}\n"
            f"  Experience: {lawyer['Experience']}\n"
            f"  Rating: {lawyer['Rating']}/5\n"
            f"  Location: {lawyer['Location']}\n"
            f"  Contact: {lawyer['Contact']}\n\n"
        )
    
    return recommendation
