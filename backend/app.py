from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from main import RAGAgent
import gc

# Configure logging with file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize agent globally but lazily
agent = None

def get_agent():
    global agent
    if agent is None:
        try:
            logger.info("Initializing RAG agent...")
            agent = RAGAgent()
            logger.info("RAG agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG agent: {e}")
            raise
    return agent

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        user_id = data.get('user_id')
        chat_id = data.get('chat_id')

        if not question or not user_id:
            return jsonify({"error": "Missing required parameters"}), 400

        # Get or initialize agent
        rag_agent = get_agent()
        
        # Retrieve chat history
        chat_history = rag_agent.get_chat_history_messages(user_id, chat_id) if chat_id else []

        # Process question with chat history
        result, references = rag_agent.run(question, user_id, chat_id, chat_history)
        
        # Extract references and process response
        answer = result
        if "\nReference:" in result:
            answer, refs = result.split("\nReference:", 1)
            references.extend([ref.strip() for ref in refs.split(',')])
            answer = answer.strip()

        response = {
            "answer": answer,
            "chat_id": chat_id,
            "references": references
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        gc.collect()

# Basic routes without complex session management
@app.route('/api/user/<user_id>/chats', methods=['GET'])
def get_user_chats(user_id):
    try:
        rag_agent = get_agent()
        chat_history = rag_agent.get_user_chat_history(user_id, "temp")
        return jsonify({
            "user_id": user_id,
            "chat_ids": chat_history,
            "count": len(chat_history)
        })
    except Exception as e:
        logger.error(f"Error retrieving chats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',  # Only allow local connections
        port=5000,
        debug=False,  
        use_reloader=False  
    )
    print(f"Backend server running at http://")