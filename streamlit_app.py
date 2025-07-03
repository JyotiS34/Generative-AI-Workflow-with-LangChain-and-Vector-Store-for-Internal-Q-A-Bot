import streamlit as st
import os
import tempfile
from typing import Dict, Any

from chatbot import DocumentationChatbot
from config import Config

# Set page config
st.set_page_config(
    page_title="Team Documentation Q&A Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_chatbot():
    """Initialize the chatbot with session state."""
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = DocumentationChatbot()
            st.session_state.chat_history = []
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()

def display_chat_message(message: Dict[str, Any], is_user: bool = False):
    """Display a chat message with proper formatting."""
    if is_user:
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["answer"])
            
            # Show sources if available
            if message.get("sources"):
                with st.expander(f"📄 Sources ({len(message['sources'])} documents)"):
                    for i, source in enumerate(message["sources"]):
                        st.write(f"**Source {i+1}:**")
                        st.write(f"File: {source['metadata'].get('file_name', 'Unknown')}")
                        st.write(f"Content: {source['content']}")
                        st.divider()

def main():
    st.title("📚 Team Documentation Q&A Chatbot")
    st.markdown("Ask questions about your team's documentation and get AI-powered answers!")
    
    # Initialize chatbot
    initialize_chatbot()
    
    # Sidebar for configuration and file management
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System information
        if st.button("ℹ️ System Info"):
            info = st.session_state.chatbot.get_system_info()
            st.json(info)
        
        st.divider()
        
        # Document management
        st.header("📁 Document Management")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['pdf', 'docx', 'doc', 'txt', 'md'],
            accept_multiple_files=True,
            help="Upload PDF, Word, or text files to add to the knowledge base"
        )
        
        if uploaded_files:
            if st.button("Process Uploaded Files"):
                with st.spinner("Processing uploaded files..."):
                    success_count = 0
                    for uploaded_file in uploaded_files:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_file_path = tmp_file.name
                        
                        try:
                            # Add document to chatbot
                            result = st.session_state.chatbot.add_document(tmp_file_path)
                            if result["status"] == "success":
                                success_count += 1
                                st.success(f"✅ {uploaded_file.name}: {result['message']}")
                            else:
                                st.error(f"❌ {uploaded_file.name}: {result['message']}")
                        except Exception as e:
                            st.error(f"❌ {uploaded_file.name}: {str(e)}")
                        finally:
                            # Clean up temporary file
                            os.unlink(tmp_file_path)
                    
                    if success_count > 0:
                        st.success(f"Successfully processed {success_count} files!")
                        st.rerun()
        
        st.divider()
        
        # Load from directory
        st.subheader("📂 Load from Directory")
        docs_dir = st.text_input("Documents Directory", value=Config.DOCS_DIRECTORY)
        
        if st.button("Load Documents from Directory"):
            with st.spinner("Loading documents..."):
                result = st.session_state.chatbot.load_documents(docs_dir)
                if result["status"] == "success":
                    st.success(result["message"])
                    if "stats" in result:
                        st.json(result["stats"])
                else:
                    st.warning(result["message"])
        
        st.divider()
        
        # Settings
        st.subheader("🔧 Settings")
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.chatbot.reset_conversation()
            st.success("Chat history cleared!")
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat with Your Documentation")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["type"] == "user":
                display_chat_message(message, is_user=True)
            else:
                display_chat_message(message, is_user=False)
    
    # Chat input
    user_question = st.chat_input("Ask a question about your documentation...")
    
    if user_question:
        # Add user message to history
        user_message = {"type": "user", "content": user_question}
        st.session_state.chat_history.append(user_message)
        
        # Display user message
        with chat_container:
            display_chat_message(user_message, is_user=True)
        
        # Get bot response
        with st.spinner("Thinking..."):
            response = st.session_state.chatbot.ask_question(user_question)
        
        # Add bot response to history
        bot_message = {"type": "bot", **response}
        st.session_state.chat_history.append(bot_message)
        
        # Display bot response
        with chat_container:
            display_chat_message(bot_message, is_user=False)
        
        # Rerun to update the display
        st.rerun()
    
    # Additional features
    st.divider()
    
    # Search functionality
    with st.expander("🔍 Advanced Search"):
        st.subheader("Search Documents")
        search_query = st.text_input("Search for specific content in documents:")
        search_k = st.slider("Number of results", min_value=1, max_value=10, value=4)
        
        if st.button("Search") and search_query:
            with st.spinner("Searching..."):
                results = st.session_state.chatbot.search_documents(search_query, k=search_k)
            
            if results:
                st.write(f"Found {len(results)} relevant documents:")
                for i, result in enumerate(results):
                    with st.expander(f"Result {i+1} (Score: {result['similarity_score']:.3f})"):
                        st.write(f"**File:** {result['metadata'].get('file_name', 'Unknown')}")
                        st.write(f"**Content:** {result['content']}")
                        st.json(result['metadata'])
            else:
                st.info("No results found.")

if __name__ == "__main__":
    main()