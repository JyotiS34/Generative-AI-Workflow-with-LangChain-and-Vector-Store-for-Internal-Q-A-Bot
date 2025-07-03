import logging
from typing import List, Dict, Any, Optional, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.base import ConversationChain
from langchain.schema import Document

from config import Config
from document_processor import DocumentProcessor
from vector_db import VectorDBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationChatbot:
    """A chatbot for answering questions about internal team documentation."""
    
    def __init__(self, db_type: str = None):
        """Initialize the chatbot with all necessary components."""
        # Validate configuration
        Config.validate_config()
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.vector_db = VectorDBManager(db_type)
        
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model_name=Config.OPENAI_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Initialize memory for conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Custom prompt template
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant that answers questions about team documentation.
            Use the following pieces of context to answer the question at the end. 
            If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
            
            Context:
            {context}
            
            Question: {question}
            
            Answer: """
        )
        
        # Initialize QA chain
        self.qa_chain = None
        self._initialize_qa_chain()
        
        logger.info("Documentation chatbot initialized successfully")
    
    def _initialize_qa_chain(self):
        """Initialize the QA chain with retriever."""
        retriever = self.vector_db.get_retriever()
        if retriever:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": self.qa_prompt},
                return_source_documents=True
            )
            logger.info("QA chain initialized")
        else:
            logger.warning("No documents loaded - QA chain not initialized")
    
    def load_documents(self, directory: str = None) -> Dict[str, Any]:
        """Load documents from a directory into the vector database."""
        logger.info("Loading documents...")
        
        # Load and process documents
        documents = self.doc_processor.load_documents(directory)
        
        if not documents:
            logger.warning("No documents found to load")
            return {"status": "warning", "message": "No documents found"}
        
        # Add to vector database
        self.vector_db.add_documents(documents)
        
        # Reinitialize QA chain
        self._initialize_qa_chain()
        
        # Get stats
        stats = self.doc_processor.get_document_stats(documents)
        
        logger.info(f"Successfully loaded {len(documents)} document chunks")
        return {
            "status": "success",
            "message": f"Loaded {len(documents)} document chunks",
            "stats": stats
        }
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a single document to the knowledge base."""
        logger.info(f"Adding document: {file_path}")
        
        try:
            # Process the document
            documents = self.doc_processor.add_document(file_path)
            
            if not documents:
                return {"status": "error", "message": "Failed to process document"}
            
            # Add to vector database
            self.vector_db.add_documents(documents)
            
            # Reinitialize QA chain
            self._initialize_qa_chain()
            
            logger.info(f"Successfully added {len(documents)} chunks from {file_path}")
            return {
                "status": "success",
                "message": f"Added {len(documents)} chunks from document",
                "chunks": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def ask_question(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """Ask a question about the documentation."""
        if not self.qa_chain:
            return {
                "status": "error",
                "message": "No documents loaded. Please load documents first.",
                "answer": "I don't have any documents to search through. Please load some documentation first."
            }
        
        try:
            logger.info(f"Processing question: {question}")
            
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            answer = result.get("result", "I couldn't find an answer to your question.")
            source_docs = result.get("source_documents", [])
            
            response = {
                "status": "success",
                "question": question,
                "answer": answer
            }
            
            if include_sources and source_docs:
                sources = []
                for i, doc in enumerate(source_docs):
                    source_info = {
                        "chunk_index": i,
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    sources.append(source_info)
                
                response["sources"] = sources
                response["num_sources"] = len(sources)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "status": "error",
                "message": str(e),
                "answer": "Sorry, I encountered an error while processing your question."
            }
    
    def search_documents(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents without generating an answer."""
        if k is None:
            k = Config.RETRIEVAL_K
        
        try:
            results = self.vector_db.search(query, k=k, with_scores=True)
            
            search_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                }
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_conversation_chain(self):
        """Get a conversation chain for multi-turn dialogue."""
        return ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False
        )
    
    def reset_conversation(self):
        """Reset the conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory reset")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the current system state."""
        return {
            "vector_db_type": self.vector_db.db_type,
            "openai_model": Config.OPENAI_MODEL,
            "chunk_size": Config.CHUNK_SIZE,
            "chunk_overlap": Config.CHUNK_OVERLAP,
            "retrieval_k": Config.RETRIEVAL_K,
            "has_qa_chain": self.qa_chain is not None,
            "docs_directory": Config.DOCS_DIRECTORY
        }