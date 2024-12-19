import csv
import datetime
import numpy as np
from sklearn.decomposition import NMF
from database import Database 
from datetime import datetime, timedelta

db = Database()
def calculate_weight(rating, experience):
    try:
        normalized_rating = float(rating) / 5
        # Handle experience as integer directly
        years = int(experience) if isinstance(experience, str) else experience
        normalized_exp = float(years) / 35 
        return (0.6 * normalized_rating + 0.4 * normalized_exp)
    except (ValueError, TypeError) as e:
        print(f"Error calculating weight: {e}")
        return 0

def get_recommendation_score(lawyer):
    try:
        lawyer_id = int(lawyer['LawyerId'])
        recommendation_history = db.get_lawyer_recommendations(lawyer_id)
        
        if not recommendation_history:
            return 0
            
        base_weight = calculate_weight(lawyer["Rating"], lawyer["Experience"])
        
        if not recommendation_history.get('LastRecommended'):
            return base_weight * 1.5
        
        last_recommended = recommendation_history['LastRecommended']
        # Ensure last_recommended is a datetime object
        if isinstance(last_recommended, str):
            last_recommended = datetime.strptime(last_recommended, '%Y-%m-%d %H:%M:%S')
            
        days_since_recommendation = (datetime.now() - last_recommended).days
        recommendation_count = int(recommendation_history.get('RecommendationCount', 0))
        
        time_factor = min(days_since_recommendation / 30.0, 1.5)
        frequency_penalty = 1.0 / (1 + (recommendation_count * 0.1))
        
        return base_weight * time_factor * frequency_penalty
    except Exception as e:
        print(f"Error calculating recommendation score: {e}")
        return 0

def update_recommendation_history(lawyer):
    try:
        # Convert LawyerId to integer
        lawyer_id = int(lawyer['LawyerId'])
        db.update_lawyer_recommendation(lawyer_id)
    except Exception as e:
        print(f"Error updating recommendation history: {e}")

def recommend_top_lawyers(sentiment):
    try:
        lawyers = db.get_lawyers_by_specialization(specialization = sentiment)
        if not lawyers:
            print("No lawyers found in database")
            return []
        scores = [(lawyer, get_recommendation_score(lawyer)) for lawyer in lawyers]
        scores.sort(key=lambda x: x[1], reverse=True)        
        top_lawyers = [lawyer for lawyer, _ in scores[:2]]
        for lawyer in top_lawyers:
            update_recommendation_history(lawyer)
        return top_lawyers

    except Exception as e:
        print(f"Error in recommend function: {e}")
        return []




if __name__ == "__main__":
    # Test the functions
    print(recommend_top_lawyers("Criminal"))
