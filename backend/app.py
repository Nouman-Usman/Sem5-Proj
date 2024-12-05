from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from main import RAGAgent
import gc
import tracemalloc
import httpx  # Add this import
# <<<<<<< HEAD
import time  # Add this import
# =======
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# >>>>>>> e71aab6bb9d18cd9af7ada11aedcdd7e1e0d801d

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
CORS(app)

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use Azure Database URI here
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# User model for SQLite (you can adjust to Azure DB model)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'
    


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
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "User already exists"}), 409

    # Hash the password
    hashed_password = generate_password_hash(password, method='sha256')

    # Create new user
    new_user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

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
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200

# Route for User Profile (Example)
@app.route('/api/user-profile', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })


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
    retries = 0
    max_retries = 3
    
    while retries < max_retries:
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

            logger.info(f"Successfully generated response for user {user_id}")
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