import uuid
from langchain.schema import BaseChatMessageHistory, BaseMessage, _message_to_dict, HumanMessage, AIMessage
from typing import Optional, List, Dict  # Add Dict to imports
from azure.data.tables import TableServiceClient, TableClient
from dotenv import load_dotenv
import os
import datetime
import json
import logging
from langchain.schema import messages_from_dict
from pprint import pprint
load_dotenv()
class AzureTableChatMessageHistory(BaseChatMessageHistory):
    CHAT_MESSAGES_TABLE = "ChatMessages"
    USER_SESSIONS_TABLE = "UserSessions"
    CHAT_TOPICS_TABLE = "ChatTopics"  
    USERS_TABLE = "Users"
    CUSTOMERS_TABLE = "Customers"
    LAWYERS_TABLE = "Lawyers"
    
    def __init__(
            self,
            chat_id: str,
            user_id: str,
            connection_string: str,
            email: str = None,  # Add email parameter
            table_name: str = "ChatMessages",
            key_prefix: str = "chat_history:"
        ):
        self.chat_id = chat_id  # Changed from chat_id
        self.user_id = user_id
        self.email = email  # Store email
        self.connection_string = connection_string
        self.key_prefix = key_prefix
        self.table_name = table_name
        self.table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
        
        # Create tables if they don't exist
        self.table_service.create_table_if_not_exists(self.CHAT_MESSAGES_TABLE)
        self.table_service.create_table_if_not_exists(self.USER_SESSIONS_TABLE)
        self.table_service.create_table_if_not_exists(self.CHAT_TOPICS_TABLE)  
        self.table_service.create_table_if_not_exists(self.table_name)
        self.table_service.create_table_if_not_exists(self.USERS_TABLE)
        self.table_service.create_table_if_not_exists(self.CUSTOMERS_TABLE)
        self.table_service.create_table_if_not_exists(self.LAWYERS_TABLE)
        
        self.messages_table = self.table_service.get_table_client(self.CHAT_MESSAGES_TABLE)
        self.sessions_table = self.table_service.get_table_client(self.USER_SESSIONS_TABLE)
        self.table_client = self.table_service.get_table_client(self.table_name)
        self.users_table = self.table_service.get_table_client(self.USERS_TABLE)
        self.customers_table = self.table_service.get_table_client(self.CUSTOMERS_TABLE)
        self.lawyers_table = self.table_service.get_table_client(self.LAWYERS_TABLE)

    def _get_message_partition_key(self) -> str:
        return f"chat_history:{self.user_id}:{self.chat_id}"
        
    def _get_session_partition_key(self) -> str:
        return f"session:{self.user_id}"

    @property
    def key(self) -> str:
        """Build partition key in format chat_history:user_id:chat_id"""
        return f"{self.key_prefix}{self.user_id}:{self.chat_id}"

    @property 
    def messages(self) -> List[BaseMessage]:
        """Get messages for current chat"""
        return self.get_chat_messages(self.user_id, self.chat_id)

    def get_chat_messages(self, user_id: str, chat_id: str) -> List[BaseMessage]:
        """Retrieve all messages for a specific chat"""
        try:
            chat_filter = f"PartitionKey eq '{self._get_message_partition_key()}'"
            entities = self.messages_table.query_entities(
                query_filter=chat_filter
            )
            messages = []
            for entity in sorted(entities, key=lambda x: x['timestamp']):
                try:
                    content = entity.get('content', '')
                    if not content:
                        continue
                    msg_type = entity.get('message_type', '')
                    if msg_type == 'HumanMessage':
                        messages.append(HumanMessage(content=content))
                    elif msg_type == 'AIMessage':
                        messages.append(AIMessage(content=content))
                        
                    logging.info(f"Retrieved {msg_type}: {content[:50]}...")
                    
                except Exception as e:
                    logging.error(f"Error processing message entity: {e}")
                    continue
            
            logging.info(f"Retrieved {len(messages)} messages for chat {chat_id}")
            return messages
            
        except Exception as e:
            logging.error(f"Error retrieving chat messages: {e}")
            raise

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat history"""
        try:
            timestamp = datetime.datetime.utcnow()
            message_id = f"{self.chat_id}_{timestamp.isoformat()}"
            
            # Ensure message has content
            if not message.content:
                logging.warning("Attempted to add empty message")
                return
                
            entity = {
                'PartitionKey': self._get_message_partition_key(),
                'RowKey': message_id,
                'user_id': self.user_id,
                'chat_id': self.chat_id,
                'timestamp': timestamp,
                'message_type': message.__class__.__name__,
                'content': message.content
            }            
            self.messages_table.create_entity(entity=entity)
            logging.info(f"Added {message.__class__.__name__} to chat {self.chat_id}: {message.content[:50]}...")
            
        except Exception as e:
            logging.error(f"Error adding message: {e}")
            raise

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

    def get_user_chats(self, user_id: str) -> List[Dict]:
        try:
            message_filter = f"user_id eq '{user_id}'"
            message_entities = list(self.messages_table.query_entities(
                query_filter=message_filter,
                select=['chat_id', 'timestamp', 'content']
            ))
            topics_table = self.table_service.get_table_client(self.CHAT_TOPICS_TABLE)
            topic_filter = f"PartitionKey eq 'chat_topic:{user_id}'"
            topic_entities = list(topics_table.query_entities(query_filter=topic_filter))
            chat_info = {}
            for msg in message_entities:
                chat_id = msg.get('chat_id')
                if chat_id:
                    if chat_id not in chat_info:
                        chat_info[chat_id] = {
                            'chat_id': chat_id,
                            'last_message': None,
                            'last_timestamp': None,
                            'message_count': 0,
                            'topic': None
                        }
                    chat_info[chat_id]['message_count'] += 1
                    msg_timestamp = msg.get('timestamp')
                    if msg_timestamp and (not chat_info[chat_id]['last_timestamp'] 
                                    or msg_timestamp > chat_info[chat_id]['last_timestamp']):
                        chat_info[chat_id]['last_timestamp'] = msg_timestamp
                        chat_info[chat_id]['last_message'] = msg.get('content', '')[:100]  # First 100 chars

            # Add topics to chat info
            for topic in topic_entities:
                chat_id = topic.get('chat_id')
                if chat_id in chat_info:
                    chat_info[chat_id]['topic'] = topic.get('topic')

            # Convert to list and sort by last_timestamp
            chats_list = list(chat_info.values())
            chats_list.sort(key=lambda x: x['last_timestamp'] or datetime.datetime.min, reverse=True)

            logging.info(f"Found {len(chats_list)} chats for user {user_id}")
            return chats_list

        except Exception as e:
            logging.error(f"Error retrieving chats for user {user_id}: {str(e)}")
            raise  # Re-raise the exception for proper error handling in the API layer

    def check_chat_exists(self, user_id: str, chat_id: str) -> bool:
        """Check if a chat exists across all relevant tables"""
        try:
            # Check messages table
            message_filter = f"user_id eq '{user_id}' and chat_id eq '{chat_id}'"
            messages_exist = any(self.messages_table.query_entities(
                query_filter=message_filter,
                select=['RowKey'],
                top=1
            ))

            # Check sessions table
            session_filter = f"user_id eq '{user_id}' and chat_id eq '{chat_id}'"
            sessions_exist = any(self.sessions_table.query_entities(
                query_filter=session_filter,
                select=['RowKey'],
                top=1
            ))

            # Check topics table
            topics_table = self.table_service.get_table_client(self.CHAT_TOPICS_TABLE)
            topic_filter = f"PartitionKey eq 'chat_topic:{user_id}' and chat_id eq '{chat_id}'"
            topics_exist = any(topics_table.query_entities(
                query_filter=topic_filter,
                select=['RowKey'],
                top=1
            ))

            return messages_exist or sessions_exist or topics_exist

        except Exception as e:
            logging.error(f"Error in check_chat_exists: {e}")
            return False

    def load_user_sessions(self, user_id: str) -> List[dict]:
        """Load all sessions for a given user"""
        try:
            user_filter = f"user_id eq '{user_id}'"
            entities = self.table_client.query_entities(
                query_filter=user_filter,
                select=['SessionData', 'RowKey']
            )
            
            sessions = []
            for entity in entities:
                if 'SessionData' in entity:
                    session_data = json.loads(entity['SessionData'])
                    sessions.append(session_data)
            return sessions
        except Exception as e:
            print(f"Error loading user sessions: {e}")
            return []

    def store_session_data(self, session_data: dict):
        entity = {
            'PartitionKey': self._get_session_partition_key(),
            'RowKey': self.chat_id,
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'timestamp': datetime.datetime.utcnow(),
            'session_data': json.dumps(session_data)
        }
        
        self.sessions_table.upsert_entity(entity=entity)

    def store_lawyer_recommendation(self, chat_id: str, lawyer_data: dict):
        """Store lawyer recommendation for a chat"""
        entity = {
            'PartitionKey': f"lawyer_rec:{self.user_id}:{chat_id}",
            'RowKey': str(uuid.uuid4()),
            'user_id': self.user_id,
            'chat_id': chat_id,
            'timestamp': datetime.datetime.utcnow(),
            'lawyer_data': json.dumps(lawyer_data)
        }
        
        try:
            self.table_client.create_entity(entity=entity)
            logging.info(f"Stored lawyer recommendation for chat {chat_id}")
        except Exception as e:
            logging.error(f"Error storing lawyer recommendation: {e}")
            raise

    def store_metadata(self, chat_id: str, metadata: dict):
        """Store metadata (lawyers and references) for a chat"""
        try:
            entity = {
                'PartitionKey': f"metadata:{self.user_id}:{chat_id}",
                'RowKey': str(uuid.uuid4()),
                'user_id': self.user_id,
                'chat_id': chat_id,
                'timestamp': datetime.datetime.utcnow(),
                'metadata': json.dumps(metadata)
            }
            
            self.table_client.create_entity(entity=entity)
            logging.info(f"Stored metadata for chat {chat_id}")
            
        except Exception as e:
            logging.error(f"Error storing metadata: {e}")
            raise

    def get_metadata(self, chat_id: str) -> Optional[dict]:
        """Retrieve metadata for a chat including both lawyers and references"""
        try:
            query_filter = f"PartitionKey eq 'metadata:{self.user_id}:{chat_id}'"
            entities = list(self.messages_table.query_entities(
                query_filter=query_filter,
                select=['metadata'],
                order_by=['timestamp desc']  # Get latest metadata
            ))
            
            if entities and 'metadata' in entities[0]:
                metadata = json.loads(entities[0]['metadata'])
                return {
                    'lawyers': metadata.get('lawyers', []),
                    'references': metadata.get('references', []),
                    'category': metadata.get('category', ''),
                    'timestamp': entities[0].get('timestamp', '').isoformat() if entities[0].get('timestamp') else None
                }
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving metadata: {e}")
            return None

    def get_chat_topics(self, user_id: str) -> List[Dict]:
        """Retrieve all chat topics for a given user"""
        try:
            table_client = self.table_service.get_table_client(self.CHAT_TOPICS_TABLE)
            query_filter = f"PartitionKey eq 'chat_topic:{user_id}'"
            entities = table_client.query_entities(query_filter=query_filter)
            topics = []
            for entity in entities:
                topics.append({
                    'chat_id': entity['chat_id'],
                    'topic': entity['topic'],
                    'timestamp': entity['timestamp']
                })
            return topics
        except Exception as e:
            logging.error(f"Error retrieving chat topics: {e}")
            return []
    def if_chat_exist(self, user_id: str, chat_id: str) -> bool:
        """Check if chat exists for a given user"""
        try:
            query_filter = f"PartitionKey eq '{self._get_message_partition_key()}' and chat_id eq '{chat_id}'"
            entities = self.messages_table.query_entities(query_filter=query_filter)
            return len(entities) > 0
        except Exception as e:
            logging.error(f"Error checking chat existence: {e}")
            return False

    def create_user(self, email: str, name: str, password: str, role: str) -> bool:
        """Create a new user"""
        try:
            entity = {
                'PartitionKey': role,
                'RowKey': email,
                'email': email,  # Add email explicitly
                'name': name,
                'password': password,
                'user_id': str(uuid.uuid4()), 
                'created_at': datetime.datetime.utcnow()
            }
            self.users_table.create_entity(entity=entity)
            return True
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return False

    def create_customer(self, user_id: str, subscription: str) -> bool:
        """Create a new customer record"""
        try:
            entity = {
                'PartitionKey': 'customer',
                'RowKey': user_id,
                'current_subscription': subscription,
                'created_at': datetime.datetime.utcnow()
            }
            self.customers_table.create_entity(entity=entity)
            return True
        except Exception as e:
            logging.error(f"Error creating customer: {e}")
            return False

    def create_lawyer(self, user_id: str) -> bool:
        """Create a new lawyer record"""
        try:
            entity = {
                'PartitionKey': 'lawyer',
                'RowKey': user_id,
                'created_at': datetime.datetime.utcnow()
            }
            self.lawyers_table.create_entity(entity=entity)
            return True
        except Exception as e:
            logging.error(f"Error creating lawyer: {e}")
            return False

    def get_user(self, email: str) -> Optional[Dict]:
        """Retrieve user by email"""
        try:
            users = self.users_table.query_entities(
                query_filter=f"RowKey eq '{email}'"
            )
            user_list = list(users)
            if user_list:
                user = user_list[0]
                return {
                    'email': user.get('email'),
                    'name': user.get('name'),
                    'user_id': user.get('user_id'),
                    'role': user.get('PartitionKey'),
                    'created_at': user.get('created_at')
                }
            return None
        except Exception as e:
            logging.error(f"Error retrieving user: {e}")
            return None

if __name__ == "__main__":
    user_id = "tese_user"
    chat_id = "test_session"
    user = AzureTableChatMessageHistory(chat_id="test_session", user_id="test_user", connection_string=os.getenv("BLOB_CONN_STRING"))
    # print (user.get_chat_messages(chat_id=chat_id, user_id=user_id))