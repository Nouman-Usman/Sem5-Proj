from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from main import RAGAgent
import gc
import tracemalloc
import httpx  # Add this import

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

if __name__ == '__main__':
    import threading
    import time

    def keep_alive():
        while True:
            time.sleep(1)

    threading.Thread(target=keep_alive).start()

    app.run(
        host='127.0.0.1',  
        port=5000,
        debug=False,  
        use_reloader=False  
    )
    print(f"Backend server running at http://")