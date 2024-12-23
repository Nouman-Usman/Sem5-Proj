import os
import gc
import json
import time  
import uuid
import httpx  
import logging
import tracemalloc
from recommend_lawyer import recommend_top_lawyers
from main import RAGAgent
from flask_cors import CORS
from datetime import datetime
from database import Database
from dotenv import load_dotenv
from datetime import timedelta
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import requests
from urllib.parse import unquote
from flask import Response, stream_with_context

load_dotenv()
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'profile_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    for stat in top_stats[:10]:
        logger.info(stat)

app = Flask(__name__)
CORS(app)

agent = None

def get_agent():
    global agent
    if agent is None:
        try:
            agent = RAGAgent()
        except Exception as e:
            raise
    return agent


app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)
jwt = JWTManager(app)

VALID_USER_TYPES = ['client', 'lawyer']


db = Database()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_image(file):
    if not file:
        return None
    
    if file and allowed_file(file.filename):
        # Create a unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        return unique_filename
    return None

# Add these helper functions after imports
def get_custom_headers(url):
    """Get custom headers based on URL domain"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,*/*'
    }
    
    if 'assets.publishing.service.gov.uk' in url:
        headers.update({
            'Accept': 'application/pdf',
            'Referer': 'https://www.gov.uk/',
            'Origin': 'https://www.gov.uk'
        })
    elif 'legislation.gov.uk' in url:
        headers.update({
            'Accept': 'application/pdf',
            'Referer': 'https://www.legislation.gov.uk/'
        })
    
    return headers

# Add this helper function
def get_pdf_with_ssl_handling(url, headers):
    """Handle PDF downloads with SSL verification options"""
    try:
        # First try with SSL verification
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        if response.status_code == 200:
            return response

        # If failed, try without SSL verification
        response = requests.get(
            url, 
            headers=headers, 
            stream=True, 
            timeout=30, 
            verify=False,
            allow_redirects=True
        )
        if response.status_code == 200:
            return response

        raise requests.RequestException(f"Failed to fetch PDF. Status: {response.status_code}")

    except requests.RequestException as e:
        raise

# ============= Chat Related Routes =============
@app.route('/api/ask', methods=['POST'])
@jwt_required()
def ask_question():
    retries = 0
    max_retries = 3
    data_loaded = False
    try:
        current_user_id = get_jwt_identity()
        role = get_jwt()['role']
        data = request.get_json()
        
        # Get session_id from request data
        question = data.get('question')
        # print(question)
        # breakpoint()
        session_id = data.get('session_id')  
        # print(session_id)
        if not question:
            return jsonify({"error": "Missing required parameter: question"}), 400
            
        # If no session_id provided, create new session
        if not session_id:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=5)
            X = vectorizer.fit_transform([question])
            key_phrases = vectorizer.get_feature_names_out()
            chat_topic = " ".join(sorted(key_phrases)).title()
            session_id = db.create_session(user_id=current_user_id, topic=chat_topic)
            data_loaded = True
            
        rag_agent = get_agent()
        history = []
        
        if session_id:
            if not data_loaded:
                history = db.get_chat_messages_by_session_id(session_id=session_id)
                data_loaded = True            

        try:
            result = rag_agent.run(question, history)
            
            # Handle tool call responses
            if isinstance(result, dict) and result.get("error"):
                return jsonify({
                    "error": "Failed to generate response",
                    "details": result.get("error_message", "Unknown error occurred")
                }), 500
                
            if not result or 'chat_response' not in result:
                return jsonify({"error": "Failed to generate response"}), 500

            # Store AI response
            sentiment = result.get('Sentiment', 'neutral')
            lawyers = recommend_top_lawyers(sentiment)
                
            lawyer_ids = [lawyer['LawyerId'] for lawyer in lawyers] if lawyers else []
            
            try:
                db.create_chat_message(
                    session_id=session_id,
                    message=result['chat_response'],
                    msg_type="AI Message",
                    recommended_lawyers=lawyer_ids,
                    references=result.get('references', [])
                )
            except Exception as e:
                print(f"Error storing chat message: {e}")
                
            response = {    
                "answer": result['chat_response'],
                "references": result.get("references", []),
                "recommended_lawyers": lawyer_ids,
                "session_id": session_id,
            }

            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": "Failed to generate response"}), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e) if app.debug else "Please try again later"
        }), 500

@app.route('/api/chat/start', methods=['POST'])
@jwt_required()
def start_chat():
    data = request.get_json()
    initiator_id = get_jwt_identity()
    recipient_id = data.get('recipient_id')
    
    if not recipient_id:
        return jsonify({"error": "Recipient ID is required"}), 400
    
    chat_id = db.create_chat_session(initiator_id, recipient_id)
    return jsonify({"chat_id": chat_id}), 201

@app.route('/api/chat/<chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    data = request.get_json()
    sender_id = get_jwt_identity()
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    db.create_chat_message(chat_id, sender_id, message)
    return jsonify({"message": "Message sent"}), 201

@app.route('/api/chat/<chat_id>/messages', methods=['GET'])
@jwt_required()
def get_chat_msg(chat_id):
    messages = db.get_chat_msg(chat_id)
    return jsonify({"messages": messages}), 200

@app.route('/api/topics', methods=['GET'])
@jwt_required()
def get_user_chats():
    try:
        user_id = get_jwt_identity()
        response = db.get_chat_topics(user_id)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch chats"}), 500

@app.route('/api/chats', methods=['GET'])
def get_chats():
    try:
        chat_sessions = db.get_all_chat_sessions()
        return jsonify({
            "chat_sessions": chat_sessions,
            "count": len(chat_sessions)
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch chat sessions"}), 500

@app.route('/api/chats/<session_id>', methods=['GET'])
def get_chat(session_id):
    try:
        chats = db.get_chat_messages_by_session_id(session_id)
        if not chats:
            return jsonify({"error": "Chat session not found"}), 404
        formatted_chats = []
        for chat in chats:
            formatted_chat = {
                "message_id": chat[0],
                "session_id": chat[1],
                "message": chat[2],
                "message_type": chat[3],
                "timestamp": chat[4].isoformat() if chat[4] else None,
                "references": json.loads(chat[5]) if chat[5] else None,
                "recommended_lawyers": json.loads(chat[6]) if chat[6] else None
            }
            formatted_chats.append(formatted_chat)
        return jsonify({
            "data": formatted_chats
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch chat session"}), 500

# ============= Auth Related Routes =============
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
        return jsonify({"error": "Failed to create user"}), 500

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
        return jsonify({"error": "Login failed"}), 500

# ============= Profile Related Routes =============
@app.route('/api/cl/profile', methods=['POST'])
@jwt_required()
def add_client_profile():
    try:
        current_user_id = get_jwt_identity()
        print(current_user_id)
        cnic = request.form.get('cnic')
        contact = request.form.get('contact')
        location = request.form.get('location')
        profile_image = request.files.get('profilePicture')

        # Validate inputs
        if not all([cnic, contact, location]):
            return jsonify({"error": "Missing required fields"}), 400
        if not cnic.isdigit() or len(cnic) != 13:
            return jsonify({"error": "Invalid CNIC format"}), 400
        if not contact.startswith('+92') or len(contact) != 13:
            return jsonify({"error": "Invalid contact number format"}), 400

        # Handle image upload separately
        image_filename = 'default.jpg'  # Default value
        if profile_image:
            if not allowed_file(profile_image.filename):
                return jsonify({"error": "Invalid file format. Allowed formats: png, jpg, jpeg, gif"}), 400
            
            image_filename = save_profile_image(profile_image)
            if not image_filename:
                return jsonify({"error": "Failed to save profile image"}), 500

        # Create client profile
        client_data = {
            'user_id': current_user_id,
            'cnic': cnic,
            'contact': contact,
            'location': location,
            'credits': 0,
            'profile_image': image_filename
        }

        if not db.create_client(**client_data):
            raise Exception("Failed to create client profile in database")

        return jsonify({
            "message": "Client profile created successfully",
            "profile": {
                "cnic": cnic,
                "contact": contact,
                "location": location,
                "profile_image": image_filename
            }
        }), 201

    except Exception as e:
        if 'image_filename' in locals() and image_filename != 'default.jpg':
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, image_filename))
            except:
                pass
        return jsonify({"error": str(e)}), 500

@app.route('/api/lw/profile', methods=['POST'])
@jwt_required()
def add_lawyer_profile():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        current_user_id = get_jwt_identity()
        
        # Check if lawyer profile already exists
        existing_lawyer = db.get_lawyer_by_user_id(current_user_id)
        if existing_lawyer:
            return jsonify({"error": "Lawyer profile already exists for this user"}), 409

        required_fields = ['cnic', 'licenseNumber', 'location', 'experience', 'specialization', 'contact', 'email']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Validate data types and formats
        try:
            experience = int(data.get('experience'))
            if experience < 0:
                raise ValueError("Experience must be a positive number")
        except (ValueError, TypeError):
            return jsonify({"error": "Experience must be a valid positive number"}), 400

        if not data['cnic'].isdigit() or len(data['cnic']) != 13:
            return jsonify({"error": "Invalid CNIC format. Must be 13 digits"}), 400

        if not '@' in data['email']:
            return jsonify({"error": "Invalid email format"}), 400

        lawyer_data = {
            'user_id': current_user_id,
            'cnic': data.get('cnic'),
            'license_number': data.get('licenseNumber'),
            'location': data.get('location'),
            'experience': experience,
            'specialization': data.get('specialization'),
            'contact': data.get('contact'),
            'email': data.get('email')
        }

        try:
            db.create_lawyer(**lawyer_data)
            logger.info(f"Successfully created lawyer profile for user ID: {current_user_id}")
            return jsonify({
                "message": "Lawyer profile created successfully",
                "status": "success",
                "user_id": current_user_id
            }), 201

        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in add_lawyer_profile: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

    finally:
        logger.debug("Finished processing lawyer profile creation request")

# App route for getting lawyer details by lawyer id
@app.route('/api/getlawyer/<lawyer_id>', methods=['GET'])
def get_lawyer_details(lawyer_id):
    try:
        if not lawyer_id:
            return jsonify({"error": "No lawyer ID provided"}), 400
            
        try:
            lawyer_id = int(lawyer_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Lawyer ID must be a valid number"}), 400

        # Get lawyer data
        lawyer = db.get_lawyer_by_id(lawyer_id)
        if not lawyer:
            return jsonify({"error": "Lawyer not found"}), 404
            
        # Convert row to dictionary with correct field mapping
        lawyer_data = {
            "LawyerId": lawyer[0],
            "Name": lawyer[1],
            "Email": lawyer[2],
            "Contact": lawyer[3],
            "Location": lawyer[4],
            "Category": lawyer[5],
            "Experience": lawyer[6],
            "Rating": float(lawyer[7]) if lawyer[7] is not None else 0.0,
            "avatar": None  # Add default avatar or handle as needed
        }
            
        return jsonify({
            "lawyer": lawyer_data
        }), 200
    except Exception as e:
        logger.error(f"Error fetching lawyer: {str(e)}")
        return jsonify({"error": "Failed to fetch lawyer"}), 500

@app.route('/api/l/profile', methods=['GET'])
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

@app.route('/api/c/profile', methods=['PUT'])
@jwt_required()
def update_client_profile():
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
            'license_number': data.get('licenseNumber', lawyer.LicenseNumber),
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

# ============= Lawyer Related Routes =============
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

@app.route('/api/lawyers/category/<specialization>', methods=['GET'])
def get_lawyers_by_category(specialization):
    try:
        lawyers = db.get_lawyers_by_specialization(specialization)
        return jsonify({
            "lawyers": [
                {
                    "name": lawyer[0],
                    "email": lawyer[1],
                    "contact": lawyer[2],
                    "experience": lawyer[3],
                    "category": lawyer[4],
                    "ratings": float(lawyer[5])
                }
                for lawyer in lawyers
            ],
            "count": len(lawyers)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching lawyers by category: {str(e)}")
        return jsonify({"error": "Failed to fetch lawyers"}), 500

@app.route('/api/lawyers/isCompleted/<user_id>', methods=['GET'])
def getIsLayerIdCompleted(user_id):
    try:
        lawyer = db.get_lawyer_by_Userid(user_id)
        if not lawyer:
            return jsonify({"is_completed": False}), 200
        return jsonify({
            "is_completed": True
        }), 200
    except Exception as e:
        logger.error(f"Error fetching lawyer: {str(e)}")
        return jsonify({"error": "Failed to fetch lawyer"}), 500

@app.route('/api/lawyers/paid', methods=['GET'])
def get_paid_lawyers():
    try:
        lawyers = db.get_paid_lawyers()
        if not lawyers:
            return jsonify({"lawyers": [], "count": 0}), 200
            
        formatted_lawyers = [
            {
                "id": lawyer[0],
                "name": lawyer[1],
                "email": lawyer[2],
                "contact": lawyer[3],
                "location": lawyer[4],
                "specialization": lawyer[5],
                "experience": lawyer[6],
                "rating": float(lawyer[7]) if lawyer[7] is not None else 0.0,
                "avatar": None
            }
            for lawyer in lawyers
        ]
        
        return jsonify({
            "lawyers": formatted_lawyers,
            "count": len(formatted_lawyers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching paid lawyers: {str(e)}")
        return jsonify({"error": "Failed to fetch lawyers"}), 500

# ============= Client Related Routes =============
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

@app.route('/api/client/isCompleted/<user_id>', methods=['GET'])
def getIsClientIdCompleted(user_id):
    try:
        client = db.get_client_by_Userid(user_id)
        if not client:
            return jsonify({"is_completed": False}), 200
        return jsonify({
            "is_completed": True
        }), 200
    except Exception as e:
        logger.error(f"Error fetching client: {str(e)}")
        return jsonify({"error": "Failed to fetch client"}), 500

# ============= Subscription Related Routes =============
@app.route('/api/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        role = get_jwt()['role']
        print(role)
        subscription_data = {
            'user_id': current_user_id,
            'subscription_type': data.get('plan'),
            'start_date': data.get('start_date'),
            'expiry_date': data.get('end_date'),
            'remaining_credits': data.get('amount')
        }
        try:
            db.create_subscription(**subscription_data)
            if (role == 'lawyer'):
                db.update_lawyer_paid_status(current_user_id)
            return jsonify({"message": "Subscription created successfully"}), 201
        except Exception as e:
            logger.error(f"Subscription creation error: {str(e)}")
            return jsonify({"error": "Failed to create subscription"}), 500
    except Exception as e:
        logger.error(f"Error in subscribe endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/subscription/current', methods=['GET'])
@jwt_required()
def get_current_subs():
    try:
        current_user_id = get_jwt_identity()
        subscription = db.get_current_subscription(current_user_id)
        if not subscription:
            return jsonify({"error": "No active subscription found"}), 404
        return jsonify({
            "subscription": subscription
        }), 200
    except Exception as e:
        logger.error(f"Error fetching current subscription: {str(e)}")
        return jsonify({"error": "Failed to fetch current subscription"}), 500

# ============= Credits Related Routes =============
@app.route('/api/get/credits/', methods=['GET'])
@jwt_required()
def get_credits():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
            
        credits = db.get_credits_by_user_id(user_id)
        
        return jsonify({
            "credits": credits,
            "user_id": user_id
        }), 200

    except Exception as e:
        logger.error(f"Error fetching credits: {str(e)}")
        return jsonify({"error": "Failed to fetch credits"}), 500

@app.route('/api/up/credits/', methods=['PUT'])
@jwt_required()
def update_credits():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
            
        data = request.get_json()
        if not isinstance(data.get('credits'), (int, float)):
            return jsonify({"error": "Invalid credits value"}), 400
            
        credits = int(data['credits'])
        if credits < 0:
            return jsonify({"error": "Credits cannot be negative"}), 400
            
        rows_updated = db.update_credits_by_user_id(user_id, credits)
        if rows_updated == 0:
            return jsonify({"error": "No active subscription found"}), 404
            
        return jsonify({
            "message": "Credits updated successfully",
            "credits": credits
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating credits: {str(e)}")
        return jsonify({"error": "Failed to update credits"}), 500

# ============= Health Check Routes =============
@app.route('/api/', methods=['GET'])
def health_check2():
    return jsonify({"status": "healthy"})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

# Update the proxy_pdf route
@app.route('/api/proxy-pdf')
def proxy_pdf():
    print("Proxy PDF")
    try:
        # Get the PDF URL from query parameter and decode it
        pdf_url = unquote(request.args.get('url', ''))
        print(pdf_url)
        # breakpoint()
        if not pdf_url:
            return jsonify({"error": "No URL provided"}), 400

        headers = get_custom_headers(pdf_url)
        
        try:
            pdf_response = get_pdf_with_ssl_handling(pdf_url, headers)
        except requests.RequestException as e:
            return jsonify({"error": str(e)}), 500

        # Set response headers
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': pdf_response.headers.get('content-type', 'application/pdf'),
            'Content-Disposition': 'inline',
            'Cache-Control': 'public, max-age=3600',
        }

        return Response(
            stream_with_context(pdf_response.iter_content(chunk_size=8192)),
            headers=response_headers
        )

    except requests.RequestException as e:
        logger.error(f"PDF proxy error: {str(e)}")
        return jsonify({"error": "Failed to fetch PDF", "details": str(e)}), 500

@app.route('/api/validate-pdf')
def validate_pdf_url():
    try:
        pdf_url = unquote(request.args.get('url', ''))
        if not pdf_url:
            return jsonify({"valid": False, "error": "No URL provided"}), 400

        response = requests.head(
            pdf_url,
            headers={'User-Agent': 'Mozilla/5.0'},
            allow_redirects=True,
            timeout=5
        )

        is_pdf = response.headers.get('content-type', '').lower().startswith('application/pdf')
        
        return jsonify({
            "valid": is_pdf and response.status_code == 200,
            "content_type": response.headers.get('content-type'),
            "size": response.headers.get('content-length')
        })

    except Exception as e:
        logger.error(f"PDF validation error: {str(e)}")
        return jsonify({"valid": False, "error": str(e)}), 500

def is_valid_uuid(uuid_str: str) -> bool:
    try:
        uuid.UUID(str(uuid_str))
        return True
    except (ValueError, AttributeError, TypeError):
        return False

def keep_alive():
    while True:
        time.sleep(1)

if __name__ == '__main__':
    import threading
    import time
    try:
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