from langchain.schema import BaseChatMessageHistory, BaseMessage, _message_to_dict, HumanMessage, AIMessage
from typing import Optional, List
from azure.data.tables import TableServiceClient, TableClient
from dotenv import load_dotenv
import os
import datetime
import json
from langchain.schema import messages_from_dict

class AzureTableChatMessageHistory(BaseChatMessageHistory):
    def __init__(
            self,
            session_id: str,
            connection_string: str,
            table_name: str = "chatHistory",
            key_prefix: str = "chat_history:"
        ):
        self.session_id = session_id
        self.connection_string = connection_string
        self.key_prefix = key_prefix
        self.table_name = table_name
        
        # Initialize Table Client
        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_service_client.create_table_if_not_exists(table_name)
        self.table_client = TableClient.from_connection_string(
            conn_str=connection_string, 
            table_name=table_name
        )

    @property
    def key(self) -> str:
        return self.key_prefix + self.session_id

    @property
    def messages(self) -> List[BaseMessage]:
        chat_history = []
        
        try:
            # Query messages for this session
            chat_history_filter = f"PartitionKey eq '{self.key}'"
            entities = self.table_client.query_entities(
                query_filter=chat_history_filter,
                select=['history', 'RowKey']
            )
            
            # Sort by timestamp (RowKey)
            sorted_entities = sorted(entities, key=lambda x: x['RowKey'])
            
            # Extract messages
            for entity in sorted_entities:
                if 'history' in entity:
                    message_dict = json.loads(entity['history'])
                    chat_history.append(message_dict)
                    
            return messages_from_dict(chat_history)
            
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []

    def add_message(self, message: BaseMessage) -> None:
        message_dict = _message_to_dict(message)
        
        # Create entity
        entity = {
            'PartitionKey': self.key,
            'RowKey': datetime.datetime.utcnow().isoformat(),
            'history': json.dumps(message_dict)
        }
        
        try:
            self.table_client.create_entity(entity=entity)
        except Exception as e:
            print(f"Error adding message: {e}")

    def clear(self) -> None:
        try:
            chat_history_filter = f"PartitionKey eq '{self.key}'"
            entities = self.table_client.query_entities(query_filter=chat_history_filter)
            for entity in entities:
                self.table_client.delete_entity(
                    partition_key=entity['PartitionKey'],
                    row_key=entity['RowKey']
                )
        except Exception as e:
            print(f"Error clearing messages: {e}")