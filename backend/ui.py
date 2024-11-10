import streamlit as st
from test import RAGAgent
import time

# Set page configuration
st.set_page_config(
    page_title="Apna Waqeel",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize RAG agent
@st.cache_resource
def get_rag_agent():
    return RAGAgent()

# Main UI
st.title("🤖 Legal Assistant")
st.markdown("""
    Welcome to your AI Legal Assistant! Ask any legal question related to Pakistani law.
""")

# Initialize agent
agent = get_rag_agent()

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What's your legal query?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.run(prompt)
            st.markdown(response)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Recommended Lawyers Section
st.markdown("---")
st.subheader("👨‍⚖️ Recommended Lawyers")

# Get recommendations if there's a query
if st.session_state.messages:
    last_query = next(msg["content"] for msg in reversed(st.session_state.messages) 
                     if msg["role"] == "user")
    recommended_lawyers = agent.get_recommended_lawyers(last_query)
    
    if recommended_lawyers:
        st.markdown("Based on your legal query, here are some recommended lawyers:")
        
        # Display lawyer cards in columns
        cols = st.columns(min(2, len(recommended_lawyers)))
        for idx, lawyer in enumerate(recommended_lawyers):
            with cols[idx % 2]:
                st.container()
                st.markdown(f"""
                <div style="padding: 1rem; border: 1px solid #ddd; border-radius: 0.5rem; margin: 0.5rem;">
                    <h3>{lawyer['Name']}</h3>
                    <p><strong>Specialization:</strong> {lawyer['Specialization']}</p>
                    <p><strong>Experience:</strong> {lawyer['Experience']}</p>
                    <p><strong>Location:</strong> {lawyer['Location']}</p>
                    <p><strong>Rating:</strong> ⭐ {lawyer['Rating']}/5</p>
                    <p><strong>Contact:</strong> <a href="tel:{lawyer['Contact']}">{lawyer['Contact']}</a></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No specific lawyers found for your query. Please try a different legal question.")
else:
    st.info("Ask a legal question to get lawyer recommendations.")

# Sidebar with information
with st.sidebar:
    st.title("About")
    st.markdown("""
    This AI Legal Assistant specializes in Pakistani law. It can help you with:
    - Legal queries and interpretations
    - Case law references
    - Legal procedures
    - General legal information
    
    The assistant uses a combination of:
    - Legal document database
    - Web search results
    - Legal context understanding
    """)
    
    # New References Section
    st.markdown("---")
    st.title("References")
    
    with st.expander("Legal Sources"):
        st.markdown("""
        🏛️ **Primary Sources**
        - Pakistan Law House Publications
        - Supreme Court Reports
        - Pakistan Legal Decisions (PLD)
        
        📚 **Secondary Sources**
        - Legal Commentaries
        - Academic Journals
        - Legal Databases
        """)
    
    with st.expander("Citation Format"):
        st.markdown("""
        **Standard Format:**
        """)
