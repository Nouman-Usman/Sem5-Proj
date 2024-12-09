from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from main import RAGAgent
import gc
import tracemalloc
import httpx  
import time  
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from crud import UserCRUD, LawyerCRUD, LawyerDetailsCRUD, ChatMessageCRUD, ChatSessionCRUD
from crud import VALID_USER_TYPES
from dotenv import load_dotenv
import uuid
from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
tracemalloc.start()

def log_memory_usage():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    logger.info("[ Top 10 memory usage ]")
    for stat in top_stats[:10]:
        logger.info(stat)

# Create Flask app
app = Flask(__name__)
CORS(app)

agent = None

def get_agent(user_id, chat_id):
    global agent
    if agent is None:
        try:
            logger.info("Initializing RAG agent...")
            agent = RAGAgent(user_id=user_id, chat_id=chat_id)
            logger.info("RAG agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG agent: {e}")
            raise
    return agent


# Configure the database and other settings
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

VALID_USER_TYPES = ['client', 'lawyer']

user_crud = UserCRUD()
lawyer_crud = LawyerCRUD()
lawyer_details_crud = LawyerDetailsCRUD()
chat_message_crud = ChatMessageCRUD()

db = Database()

# Route for Signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'client').lower()
    user_id = str(uuid.uuid4())
    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if role not in ['client', 'lawyer']:
        return jsonify({"error": "Invalid role. Must be either 'client' or 'lawyer'"}), 400

    try:
        hashed_password = generate_password_hash(password)
        user_created = db.create_user(name, email, hashed_password, role)
        if not user_created:
            return jsonify({"error": "Failed to create user"}), 500
        user = db.get_user_by_email(email)
        if not user:
            return jsonify({"error": "User created but failed to retrieve"}), 500
        access_token = create_access_token(
            identity=user.UserId,
            additional_claims={
                "role": role,
                "email": email,
                "name": name,
                "user_id": user_id
            }
        )

        return jsonify({
            "message": "User created successfully",
            "access_token": access_token,
            "user": {
                "id": user.UserId,
                "email": email,
                "name": name,
                "role": role
            }
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "Failed to create user"}), 500

# Route for Login
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    
    try:
        user = db.get_user_by_email(email)
        if not user or not check_password_hash(user.Password, password):
            return jsonify({"error": "Invalid credentials"}), 401
        access_token = create_access_token(
            identity=user.UserId,
            additional_claims={
                "role": user.Role,
                "email": user.Email,
                "name": user.Name,
                "user_id": user.UserId
            }
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.UserId,
                "email": user.Email,
                "name": user.Name,
                "role": user.Role,                 
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500

# Route for adding client profile
@app.route('/api/cl/profile', methods=['POST'])
@jwt_required()
def add_client_profile():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    client_data = {
        'user_id': current_user_id,
        'cnic': data.get('cnic'),
        'contact': data.get('contact'),
        'location': data.get('location')
    }
    try:
        db.create_client(**client_data)
        return jsonify({"message": "Client profile created successfully"}), 201
    except Exception as e:
        logger.error(f"Client profile creation error: {str(e)}")
        return jsonify({"error": "Failed to create client profile"}), 500

# Route for adding lawyer profile
@app.route('/api/lw/profile', methods=['POST'])
@jwt_required()
def add_lawyer_profile():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    lawyer_data = {
        'user_id': current_user_id,
        'cnic': data.get('cnic'),
        'license_number': data.get('license_number'),
        'location': data.get('location'),
        'experience': data.get('experience'),
        'specialization': data.get('specialization'),
        'contact': data.get('contact'),
        'email': data.get('email')
    }
    try:
        db.create_lawyer(**lawyer_data)
        return jsonify({"message": "Lawyer profile created successfully"}), 201
    except Exception as e:
        logger.error(f"Lawyer profile creation error: {str(e)}")
        return jsonify({"error": "Failed to create lawyer profile"}), 500
    
# Route for fetching user profile
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = db.get_user_by_id(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.Role == 'client':
        client = db.get_client_by_user_id(current_user_id)
        if not client:
            return jsonify({"error": "Client profile not found"}), 404
        return jsonify({
            "user": {
                "id": user.UserId,
                "email": user.Email,
                "name": user.Name,
                "role": user.Role
            },
            "client": {
                "cnic": client.CNIC,
                "contact": client.Contact,
                "location": client.Location
            }
        }), 200
    else:
        lawyer = db.get_lawyer_by_user_id(current_user_id)
        if not lawyer:
            return jsonify({"error": "Lawyer profile not found"}), 404
        return jsonify({
            "user": {
                "id": user.UserId,
                "email": user.Email,
                "name": user.Name,
                "role": user.Role
            },
            "lawyer": {
                "cnic": lawyer.CNIC,
                "license_number": lawyer.LicenseNumber,
                "location": lawyer.Location,
                "experience": lawyer.Experience,
                "specialization": lawyer.Specialization,
                "contact": lawyer.Contact,
                "email": lawyer.Email
            }
        }), 200

# Route for updating user profile
@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = db.get_user_by_id(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.Role == 'client':
        client = db.get_client_by_user_id(current_user_id)
        if not client:
            return jsonify({"error": "Client profile not found"}), 404
        client_data = {
            'user_id': current_user_id,
            'cnic': data.get('cnic', client.CNIC),
            'contact': data.get('contact', client.Contact),
            'location': data.get('location', client.Location)
        }
        try:
            db.update_client(**client_data)
            return jsonify({"message": "Client profile updated successfully"}), 200
        except Exception as e:
            logger.error(f"Client profile update error: {str(e)}")
            return jsonify({"error": "Failed to update client profile"}), 500
    else:
        lawyer = db.get_lawyer_by_user_id(current_user_id)
        if not lawyer:
            return jsonify({"error": "Lawyer profile not found"}), 404
        lawyer_data = {
            'user_id': current_user_id,
            'cnic': data.get('cnic', lawyer.CNIC),
            'license_number': data.get('license_number', lawyer.LicenseNumber),
            'location': data.get('location', lawyer.Location),
            'experience': data.get('experience', lawyer.Experience),
            'specialization': data.get('specialization', lawyer.Specialization),
            'contact': data.get('contact', lawyer.Contact),
            'email': data.get('email', lawyer.Email)
        }
        try:
            db.update_lawyer(**lawyer_data)
            return jsonify({"message": "Lawyer profile updated successfully"}), 200
        except Exception as e:
            logger.error(f"Lawyer profile update error: {str(e)}")
            return jsonify({"error": "Failed to update lawyer profile"}), 500
    
# Route for fetching all lawyers
@app.route('/api/lawyers', methods=['GET'])
def get_lawyers():
    try:
        lawyers = db.get_all_lawyers()
        return jsonify({
            "lawyers": lawyers,
            "count": len(lawyers)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching lawyers: {str(e)}")
        return jsonify({"error": "Failed to fetch lawyers"}), 500

# Route for fetching a single lawyer
@app.route('/api/lawyers/<lawyer_id>', methods=['GET'])
def get_lawyer(lawyer_id):
    try:
        lawyer = db.get_lawyer_by_id(lawyer_id)
        if not lawyer:
            return jsonify({"error": "Lawyer not found"}), 404
        return jsonify({
            "lawyer": lawyer
        }), 200
    except Exception as e:
        logger.error(f"Error fetching lawyer: {str(e)}")
        return jsonify({"error": "Failed to fetch lawyer"}), 500
    
# Route for fetching all clients
@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        clients = db.get_all_clients()
        return jsonify({
            "clients": clients,
            "count": len(clients)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        return jsonify({"error": "Failed to fetch clients"}), 500
    
# Route for fetching a single client
@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client(client_id):
    try:
        client = db.get_client_by_id(client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404
        return jsonify({
            "client": client
        }), 200
    except Exception as e:
        logger.error(f"Error fetching client: {str(e)}")
        return jsonify({"error": "Failed to fetch client"}), 500

# Route for fetching all chat sessions
@app.route('/api/chats', methods=['GET'])
def get_chats():
    try:
        chat_sessions = db.get_all_chat_sessions()
        return jsonify({
            "chat_sessions": chat_sessions,
            "count": len(chat_sessions)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {str(e)}")
        return jsonify({"error": "Failed to fetch chat sessions"}), 500

# Route for fetching a single chat session
@app.route('/api/chats/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    try:
        chat_session = db.get_chat_session_by_id(chat_id)
        if not chat_session:
            return jsonify({"error": "Chat session not found"}), 404
        return jsonify({
            "chat_session": chat_session
        }), 200
    except Exception as e:
        logger.error(f"Error fetching chat session: {str(e)}")
        return jsonify({"error": "Failed to fetch chat session"}), 500

# Route for fetching all chat messages
@app.route('/api/chat/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    try:
        chat_messages = db.get_chat_messages_by_chat_id(chat_id)
        return jsonify({
            "chat_messages": chat_messages,
            "count": len(chat_messages)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching chat messages: {str(e)}")
        return jsonify({"error": "Failed to fetch chat messages"}), 500

# Route for fetching a single chat message
@app.route('/api/chat/<chat_id>/messages/<message_id>', methods=['GET'])
def get_chat_message(chat_id, message_id):
    try:
        chat_message = db.get_chat_message_by_id(message_id)
        if not chat_message:
            return jsonify({"error": "Chat message not found"}), 404
        return jsonify({
            "chat_message": chat_message
        }), 200
    except Exception as e:
        logger.error(f"Error fetching chat message: {str(e)}")
        return jsonify({"error": "Failed to fetch chat message"}), 500

# Route for adding a chat message
@app.route('/api/chat/<chat_id>/messages', methods=['POST'])
@jwt_required()
def add_chat_message(chat_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    chat_message_data = {
        'chat_id': chat_id,
        'user_id': current_user_id,
        'message': data.get('message')
    }
    try:
        db.create_chat_message(**chat_message_data)
        return jsonify({"message": "Chat message created successfully"}), 201
    except Exception as e:
        logger.error(f"Chat message creation error: {str(e)}")
        return jsonify({"error": "Failed to create chat message"}), 500

# Route for updating a chat message
@app.route('/api/chat/<chat_id>/messages/<message_id>', methods=['PUT'])
@jwt_required()
def update_chat_message(chat_id, message_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    chat_message_data = {
        'chat_id': chat_id,
        'user_id': current_user_id,
        'message': data.get('message')
    }
    try:
        db.update_chat_message(message_id, **chat_message_data)
        return jsonify({"message": "Chat message updated successfully"}), 200
    except Exception as e:
        logger.error(f"Chat message update error: {str(e)}")
        return jsonify({"error": "Failed to update chat message"}), 500



@app.route('/api/', methods=['GET'])
def health_check2():
    return jsonify({"status": "healthy"})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

def is_valid_uuid(uuid_str: str) -> bool:
    try:
        uuid.UUID(str(uuid_str))
        return True
    except (ValueError, AttributeError, TypeError):
        return False

@app.route('/api/ask', methods=['POST'])
@jwt_required()  # Add this decorator to require authentication
def ask_question():
    result = None
    retries = 0
    max_retries = 3
    
    while retries < max_retries:
        try:
            current_user_id = get_jwt_identity()
            
            data = request.get_json()
            if not data:
                logger.error("No JSON data received")
                return jsonify({"error": "No data provided"}), 400

            question = data.get('question')
            # chat_id = data.get('chat_id')
            chat_id = "9AB8CE33-46AD-4EAE-B77A-2182B97DD4BA"
            # if not chat_id:
            #     chat_session_crud = ChatSessionCRUD()
            #     chat_id = chat_session_crud.create(
            #         initiator_id=current_user_id,
            #         recipient_id="00000000-0000-0000-0000-000000000000"
            #     )
            #     if not chat_id:
            #         raise Exception("Failed to create chat session")
            if not question:
                logger.error("Missing question parameter")
                return jsonify({"error": "Missing required parameter: question"}), 400
            logger.info(f"Processing question for user {current_user_id}, chat {chat_id}")            
            rag_agent = get_agent(user_id=current_user_id, chat_id=chat_id)
            chat_id_str = str(chat_id) if chat_id else None
            if chat_id_str and is_valid_uuid(chat_id_str) and is_valid_uuid(current_user_id):
                chat_history = chat_message_crud.get_chat_messages(
                    user_id=current_user_id,
                    chat_id=chat_id_str
                )
            else:
                logger.warning(f"Invalid UUID - chat_id: {chat_id_str}, user_id: {current_user_id}")
                chat_history = []            
            result = rag_agent.run(question, current_user_id, chat_id_str, chat_history)
            
            if not result or 'chat_response' not in result:
                logger.error("Invalid result from RAG agent")
                retries += 1
                if retries == max_retries:
                    return jsonify({"error": "Failed to generate response"}), 500
                time.sleep(1)
                continue

            response = {
                "answer": result["chat_response"],
                "chat_id": chat_id or "new_chat",
                "references": result.get("references", []),
                "recommended_lawyers": result.get("recommended_lawyers", [])
            }

            # Validate response
            if not response["answer"]:
                logger.error("Empty response generated")
                retries += 1
                if retries == max_retries:
                    return jsonify({"error": "Empty response generated"}), 500
                time.sleep(1)
                continue

            logger.info(f"Successfully generated response for user {current_user_id}")
            return jsonify(response), 200

        except Exception as e:
            logger.error(f"Error processing question (attempt {retries + 1}): {str(e)}", exc_info=True)
            retries += 1
            if retries == max_retries:
                return jsonify({"error": str(e)}), 500
            time.sleep(1)
            continue
        finally:
            if 'data' in locals(): del data
            if 'question' in locals(): del question
            if 'user_id' in locals(): del user_id
            if 'chat_id' in locals(): del chat_id
            if 'rag_agent' in locals(): del rag_agent
            if 'chat_history' in locals(): del chat_history
            if result:
                del result
            gc.collect()
            log_memory_usage()

@app.route('/api/user/<user_id>/chats/<chat_id>', methods=['GET'])
def get_user_chats(user_id, chat_id):
    try:
        rag_agent = get_agent(user_id=user_id, chat_id=chat_id)

        chat_history = rag_agent.get_user_chat_history(user_id, chat_id=chat_id)
        # return jsonify({
        #     "user_id": user_id,
        #     "chat_ids": chat_history,
        #     "count": len(chat_history)
        # })
        return None
    except Exception as e:
        logger.error(f"Error retrieving chats: {e}")
        return jsonify({"error": str(e)}), 500

# @app.route('/api/lawyer/register', methods=['POST'])
# @jwt_required()
# def register_lawyer():
#     try:
#         data = request.get_json()
#         lawyer_store = LawyerStore(connection_string=os.getenv("SQL_CONN_STRING"))
        
#         lawyer_data = {
#             "name": data["name"],
#             "email": data["email"],
#             "specialization": data["specialization"],
#             "experience": data["experience"],
#             "license_number": data["license_number"],
#             "rating": 0.0,  # Default rating for new lawyers
#             "location": data["location"],
#             "specializations": data.get("specializations", [])
#         }
        
#         lawyer_store.add_lawyer(lawyer_data)
#         return jsonify({"message": "Lawyer registered successfully"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/api/chat/start', methods=['POST'])
@jwt_required()
# def start_chat():
#     try:
#         data = request.get_json()
#         initiator_id = get_jwt_identity()
#         recipient_id = data.get('recipient_id', "00000000-0000-0000-0000-000000000000")  # Default to system ID
        
#         # Get agent instance to use its methods
#         agent = get_agent(initiator_id, None)
        
#         # Ensure both users exist
#         if not (agent.ensure_user_exists(initiator_id) and agent.ensure_user_exists(recipient_id)):
#             return jsonify({"error": "Failed to ensure users exist"}), 500
        
#         chat_id = str(uuid.uuid4())
#         conn = pyodbc.connect(os.getenv("SQL_CONN_STRING"))
#         cursor = conn.cursor()
        
#         query = """
#             INSERT INTO ChatSessions 
#             (ChatId, InitiatorId, RecipientId, Status, StartTime)
#             VALUES (?, ?, ?, 'Active', GETDATE())
#         """
#         cursor.execute(query, (chat_id, initiator_id, recipient_id))
#         conn.commit()
        
#         return jsonify({"chat_id": chat_id}), 201
#     except Exception as e:
#         logger.error(f"Error starting chat: {e}")
#         return jsonify({"error": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()

def keep_alive():
    while True:
        time.sleep(1)

if __name__ == '__main__':
    import threading
    import time
    try:
        # Start the keep_alive thread
        threading.Thread(target=keep_alive, daemon=True).start()

        # Run the Flask app
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,  # Disable in production
            use_reloader=False  # Set to False in production
        )
        print("Backend server started...")
    except KeyboardInterrupt:
        print("\nServer stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"An error occurred: {e}")