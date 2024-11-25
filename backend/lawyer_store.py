from azure.data.tables import TableServiceClient, TableClient
from typing import List, Dict, Optional
import datetime
import json
import os
import csv
import uuid
import logging
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableServiceClient, TableClient

load_dotenv()


class LawyerStore:
    LAWYERS_TABLE = "LawyerRecommendations"

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.table_service = TableServiceClient.from_connection_string(
            conn_str=connection_string
        )
        self.table_service.create_table_if_not_exists(self.LAWYERS_TABLE)
        self.table_client = TableClient.from_connection_string(
            conn_str=connection_string, table_name=self.LAWYERS_TABLE
        )
        # self._load_lawyers_from_csv()

    # def _load_lawyers_from_csv(self):
    #     """Load lawyers from CSV and store in Azure Table"""
    #     try:
    #         with open("lawyers.csv", mode="r", encoding='utf-8') as file:
    #             lawyers = csv.DictReader(file)
    #             for lawyer in lawyers:
    #                 lawyer_id = str(uuid.uuid4())
    #                 self.add_lawyer({
    #                     'lawyer_id': lawyer_id,
    #                     'name': lawyer['Name'],
    #                     'specialization': lawyer['Specialization'],
    #                     'experience': lawyer['Experience'],
    #                     'rating': lawyer['Rating'],
    #                     'location': lawyer['Location'],
    #                     'contact': lawyer['Contact']
    #                 })
    #         logging.info("Successfully loaded lawyers from CSV")
    #     except Exception as e:
    #         logging.error(f"Error loading lawyers from CSV: {e}")

    def calculate_weight(self, rating: str, experience: str) -> float:
        """Calculate weight for lawyer ranking"""
        try:
            normalized_rating = float(rating) / 5
            years = int(experience.split()[0])
            normalized_exp = float(years) / 35
            return 0.6 * normalized_rating + 0.4 * normalized_exp
        except (ValueError, IndexError) as e:
            logging.error(f"Error calculating weight: {e}")
            return 0

    def get_top_lawyers(self, category: str, limit: int = 2) -> List[Dict]:
        """Get top N lawyers by category based on rating and experience"""
        lawyers = self.get_lawyers_by_category(category)

        # Calculate weights and sort
        weighted_lawyers = []
        for lawyer in lawyers:
            weight = self.calculate_weight(lawyer["rating"], lawyer["experience"])
            weighted_lawyers.append((lawyer, weight))

        # Sort by weight and return top N
        top_lawyers = sorted(weighted_lawyers, key=lambda x: x[1], reverse=True)[:limit]
        return [lawyer for lawyer, _ in top_lawyers]

    def format_recommendation(self, lawyers: List[Dict]) -> Dict:
        """Format lawyer recommendations with detailed info"""
        formatted = []
        for lawyer in lawyers:
            formatted.append({
                "name": lawyer["name"],
                "specialization": lawyer["specialization"],
                "experience": lawyer["experience"],
                "rating": lawyer["rating"],
                "location": lawyer["location"],
                "contact": lawyer["contact"],
                "recommended_for": lawyer["specialization"],
                "recommendation_score": self.calculate_weight(lawyer["rating"], lawyer["experience"])
            })
        return formatted

    def add_lawyer(self, lawyer_data: Dict) -> None:
        entity = {
            "PartitionKey": f"recommendation:{lawyer_data['specialization']}",
            "RowKey": lawyer_data["lawyer_id"],
            "lawyer_name": lawyer_data["name"],
            "specialization": lawyer_data["specialization"],
            "experience": lawyer_data["experience"],
            "rating": lawyer_data["rating"],
            "location": lawyer_data["location"],
            "contact": lawyer_data["contact"],
        }

        self.table_client.upsert_entity(entity=entity)

    def get_lawyers_by_category(self, category: str) -> List[Dict]:
        lawyers = []
        query_filter = f"PartitionKey eq 'recommendation:{category}'"

        entities = self.table_client.query_entities(query_filter=query_filter)
        for entity in entities:
            lawyers.append(
                {
                    "name": entity["lawyer_name"],
                    "specialization": entity["specialization"],
                    "experience": entity["experience"],
                    "rating": entity["rating"],
                    "location": entity["location"],
                    "contact": entity["contact"],
                }
            )

        return lawyers

    def update_lawyer(self, lawyer_id: str, lawyer_data: Dict) -> None:
        entity = self.table_client.get_entity(
            partition_key=f"recommendation:{lawyer_data['specialization']}",
            row_key=lawyer_id,
        )

        for key, value in lawyer_data.items():
            if key not in ["PartitionKey", "RowKey"]:
                entity[key] = value

        self.table_client.update_entity(entity=entity)

    def delete_lawyer(self, category: str, lawyer_id: str) -> None:
        self.table_client.delete_entity(
            partition_key=f"recommendation:{category}", row_key=lawyer_id
        )


if __name__ == "__main__":
    user = LawyerStore(connection_string=os.getenv("BLOB_CONN_STRING"))
    print(user.get_top_lawyers("Banking and Finance", limit=3))
