from azure.data.tables import TableServiceClient, TableClient
from datetime import datetime, timedelta

class AzureChatSummaryStorage:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.table_name = "chatsummaries"
        self._ensure_table_exists()
        self.max_summary_age = timedelta(hours=24)  # Configure max age for summaries

    def _ensure_table_exists(self):
        table_service = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_service.create_table(self.table_name)
        except Exception:
            pass

    def save_summary(self, chat_id: str, summary: str, merge: bool = True):
        table_client = TableClient.from_connection_string(
            self.connection_string, 
            self.table_name
        )
        
        existing_summary = ''
        access_count = 0
        
        if merge:
            # Try to get existing summary
            try:
                existing = table_client.get_entity('summary', chat_id)
                existing_summary = existing.get('summary', '')
                access_count = existing.get('access_count', 0)
                existing_timestamp = datetime.fromisoformat(existing.get('timestamp'))
                
                # Check if existing summary is still relevant (within max age)
                if datetime.utcnow() - existing_timestamp < self.max_summary_age:
                    # Merge summaries
                    summary = f"{existing_summary}\n---\nUpdated context: {summary}"
            except Exception:
                pass  # No existing summary or error reading it
        
        entity = {
            'PartitionKey': 'summary',
            'RowKey': chat_id,
            'summary': summary,
            'timestamp': datetime.utcnow().isoformat(),
            'access_count': access_count + 1
        }
        
        table_client.upsert_entity(entity)

    def get_summary(self, chat_id: str) -> dict:
        table_client = TableClient.from_connection_string(
            self.connection_string, 
            self.table_name
        )
        
        try:
            entity = table_client.get_entity('summary', chat_id)
            timestamp = datetime.fromisoformat(entity.get('timestamp'))
            
            # Update access count
            entity['access_count'] = entity.get('access_count', 0) + 1
            table_client.update_entity(entity)
            
            # Check if summary is still relevant
            if datetime.utcnow() - timestamp > self.max_summary_age:
                return {"summary": "Previous conversation has expired.", "expired": True}
                
            return {
                "summary": entity.get('summary', "No previous conversation."),
                "expired": False,
                "access_count": entity.get('access_count', 0)
            }
        except Exception:
            return {"summary": "No previous conversation.", "expired": False, "access_count": 0}

    def delete_summary(self, chat_id: str):
        table_client = TableClient.from_connection_string(
            self.connection_string, 
            self.table_name
        )
        
        try:
            table_client.delete_entity('summary', chat_id)
        except Exception:
            pass