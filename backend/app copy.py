from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from main import RAGAgent
import gc
import tracemalloc
import httpx  # Add this import
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Start tracing memory allocations
tracemalloc.start()

def log_memory_usage():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    logger.info("[ Top 10 memory usage ]")
    for stat in top_stats[:10]:
        logger.info(stat)

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Set a secret key for JWT
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

# Initialize JWTManager
jwt = JWTManager(app)

# Initialize agent globally but lazily
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

    


# api routes for front end

# Route for Signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'client')  # Default to 'client' if role is not provided

    # Validate input
    if not all([name, email, password, role]):
        return jsonify({"error": "Missing data"}), 400

    # Check if user already exists
    if (False):
        return jsonify({"error": "User already exists"}), 409

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Create new user
        # some code to save user

    return jsonify({"message": "User created successfully"}), 201

# Route for Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate input
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    # Find user by email
    
    # if not user or not check_password_hash(user.password, password):  ## if user donot exists or invalid credentials 
        # return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    access_token = create_access_token(
        identity="123",  ## put user id here
        additional_claims={"role": "customer"}   ## put user role here
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200

# Route for User Profile (Example)
@app.route('/api/user-profile', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get("role")
    current_user_id = get_jwt_identity()
    if user_role == "lawyer":
        # Handle logic for lawyer role
        return jsonify({
            "message": "Hello, Lawyer",
            "user_id": current_user_id
        })
    elif user_role == "customer":
        # Handle logic for customer role
        return jsonify({
            "message": "Hello, Customer",
            "user_id": current_user_id
        })
    else:
        return jsonify({"message": "Invalid role"}), 403


# Route for verifying token
@app.route('/api/verify-token', methods=['POST'])
@jwt_required()  # This will automatically get the token from the Authorization header
def verify_token():
    # The token is already verified by @jwt_required, so no need to manually check it
    current_user = get_jwt_identity()  # This gets the user info stored in the token (e.g., user ID, role)
   
    if not current_user:
        return jsonify({"message": "Invalid or expired token!"}), 401

    # Check the role of the user
    if current_user.get('role') == 'lawyer':
        return jsonify({"role": 'lawyer'}), 200
    elif current_user.get('role') == 'customer':
        return jsonify({"role": 'customer'}), 200
    else:
        return jsonify({"message": "Unauthorized access!"}), 403



@app.route('/api/', methods=['GET'])
def health_check2():
    return jsonify({"status": "healthy"})




###########


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/ask', methods=['POST'])
def ask_question():
    result = None 
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No data provided"}), 400

        question = data.get('question')
        user_id = data.get('user_id')
        chat_id = data.get('chat_id')

        if not question or not user_id:
            logger.error(f"Missing parameters: question={bool(question)}, user_id={bool(user_id)}")
            return jsonify({"error": "Missing required parameters"}), 400

        logger.info(f"Processing question for user {user_id}, chat {chat_id}")
        
        rag_agent = get_agent(user_id=user_id, chat_id=chat_id)
        chat_history = rag_agent.get_chat_history_messages(user_id, chat_id) if chat_id else []

        result = rag_agent.run(question, user_id, chat_id, chat_history)
        
        if not result or 'chat_response' not in result:
            logger.error("Invalid result from RAG agent")
            return jsonify({"error": "Failed to generate response"}), 500

        response = {
            "answer": result["chat_response"],
            "chat_id": chat_id or "new_chat",
            "references": result.get("references", []),
            "recommended_lawyers": result.get("recommended_lawyers", [])
        }

        logger.info(f"Successfully generated response for user {user_id}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        del data, question, user_id, chat_id, rag_agent, chat_history
        if result:
            del result
        gc.collect()
        log_memory_usage()  # Log memory usage after each request

# Basic routes without complex session management
@app.route('/api/user/<user_id>/chats/<chat_id>', methods=['GET'])
def get_user_chats(user_id, chat_id):
    try:
        rag_agent = get_agent(user_id=user_id, chat_id=chat_id)
        chat_history = rag_agent.get_user_chat_history(user_id, chat_id=chat_id)
        return jsonify({
            "user_id": user_id,
            "chat_ids": chat_history,
            "count": len(chat_history)
        })
    except Exception as e:
        logger.error(f"Error retrieving chats: {e}")
        return jsonify({"error": str(e)}), 500


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