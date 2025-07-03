import os
import pickle
import logging
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod

import chromadb
from chromadb.config import Settings

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBInterface(ABC):
    """Abstract interface for vector databases."""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector database."""
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search."""
        pass
    
    @abstractmethod
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Perform similarity search with scores."""
        pass
    
    @abstractmethod
    def delete_documents(self, source_file: str = None) -> None:
        """Delete documents from the database."""
        pass

class ChromaVectorDB(VectorDBInterface):
    """Chroma vector database implementation."""
    
    def __init__(self, embeddings: OpenAIEmbeddings):
        self.embeddings = embeddings
        self.persist_directory = Config.CHROMA_PERSIST_DIRECTORY
        
        # Initialize Chroma
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
        logger.info(f"Initialized Chroma database at {self.persist_directory}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Chroma."""
        if documents:
            self.vectorstore.add_documents(documents)
            self.vectorstore.persist()
            logger.info(f"Added {len(documents)} documents to Chroma")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search in Chroma."""
        return self.vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Perform similarity search with scores in Chroma."""
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def delete_documents(self, source_file: str = None) -> None:
        """Delete documents from Chroma (limited functionality)."""
        logger.warning("Chroma doesn't support easy document deletion. Consider recreating the database.")

class VectorDBManager:
    """Manager class for vector database operations."""
    
    def __init__(self, db_type: str = None):
        self.embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        
        if db_type is None:
            db_type = Config.VECTOR_DB_TYPE
        
        if db_type.lower() == "chroma":
            self.db = ChromaVectorDB(self.embeddings)
        else:
            # Default to Chroma if unsupported type is specified
            logger.warning(f"Unsupported vector database type: {db_type}. Defaulting to Chroma.")
            self.db = ChromaVectorDB(self.embeddings)
            db_type = "chroma"
        
        self.db_type = db_type
        logger.info(f"Initialized {db_type} vector database")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector database."""
        return self.db.add_documents(documents)
    
    def search(self, query: str, k: int = None, with_scores: bool = False) -> List:
        """Search for similar documents."""
        if k is None:
            k = Config.RETRIEVAL_K
        
        if with_scores:
            return self.db.similarity_search_with_score(query, k=k)
        else:
            return self.db.similarity_search(query, k=k)
    
    def delete_documents(self, source_file: str = None) -> None:
        """Delete documents from the database."""
        return self.db.delete_documents(source_file)
    
    def get_retriever(self, k: int = None):
        """Get a retriever object for use with LangChain."""
        if k is None:
            k = Config.RETRIEVAL_K
            
        if hasattr(self.db, 'vectorstore') and self.db.vectorstore:
            return self.db.vectorstore.as_retriever(search_kwargs={"k": k})
        else:
            logger.warning("No documents in vector database")
            return None