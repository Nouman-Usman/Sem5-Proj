import csv
import numpy as np
from sklearn.decomposition import NMF

def calculate_weight(rating, experience):
    try:
        normalized_rating = float(rating) / 5
        years = int(experience.split()[0]) 
        normalized_exp = float(years) / 35 
        return (0.6 * normalized_rating + 0.4 * normalized_exp)
    except (ValueError, IndexError) as e:
        print(f"Error calculating weight: {e}")
        return 0

def load_lawyer_data():
    try:
        with open("lawyers.csv", mode="r", encoding='utf-8') as file:
            lawyers = list(csv.DictReader(file))
        return lawyers
    except Exception as e:
        print(f"Error loading lawyer data: {e}")
        return []

def create_rating_matrix(lawyers):
    categories = list(set(lawyer["Specialization"].strip() for lawyer in lawyers))
    lawyer_names = [lawyer["Name"] for lawyer in lawyers]
    rating_matrix = np.zeros((len(lawyer_names), len(categories)))

    for i, lawyer in enumerate(lawyers):
        category_index = categories.index(lawyer["Specialization"].strip())
        rating_matrix[i, category_index] = float(lawyer["Rating"])

    return rating_matrix, lawyer_names, categories

def recommend(category):
    try:
        lawyers = load_lawyer_data()
        if not lawyers:
            print("No lawyers found in database")
            return []

        rating_matrix, lawyer_names, categories = create_rating_matrix(lawyers)
        category_index = categories.index(category)

        model = NMF(n_components=2, init='random', random_state=0)
        W = model.fit_transform(rating_matrix)
        H = model.components_

        category_scores = H[:, category_index]
        top_indices = np.argsort(category_scores)[-2:][::-1]
        top_lawyers = [lawyers[i] for i in top_indices]

        return top_lawyers

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
