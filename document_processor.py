import os
import logging
from typing import List, Dict, Any
from pathlib import Path

from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process and chunk documents for vector storage."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Supported file extensions and their loaders
        self.file_loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader,
            '.txt': TextLoader,
            '.md': TextLoader,
        }
    
    def load_documents(self, directory: str = None) -> List[Document]:
        """Load all supported documents from a directory."""
        if directory is None:
            directory = Config.DOCS_DIRECTORY
            
        documents = []
        
        if not os.path.exists(directory):
            logger.warning(f"Documents directory {directory} does not exist")
            return documents
        
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.file_loaders:
                try:
                    docs = self.load_single_document(str(file_path))
                    documents.extend(docs)
                    logger.info(f"Loaded {len(docs)} chunks from {file_path}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def load_single_document(self, file_path: str) -> List[Document]:
        """Load and process a single document."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.file_loaders:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        loader_class = self.file_loaders[file_extension]
        
        try:
            loader = loader_class(file_path)
            raw_documents = loader.load()
            
            # Add metadata
            for doc in raw_documents:
                doc.metadata.update({
                    'source_file': file_path,
                    'file_type': file_extension,
                    'file_name': Path(file_path).name
                })
            
            # Split documents into chunks
            documents = self.text_splitter.split_documents(raw_documents)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def add_document(self, file_path: str) -> List[Document]:
        """Add a single document to the knowledge base."""
        return self.load_single_document(file_path)
    
    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """Get statistics about the loaded documents."""
        if not documents:
            return {}
        
        file_types = {}
        source_files = set()
        total_chars = 0
        
        for doc in documents:
            # Count file types
            file_type = doc.metadata.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # Track source files
            source_files.add(doc.metadata.get('source_file', 'unknown'))
            
            # Count characters
            total_chars += len(doc.page_content)
        
        return {
            'total_chunks': len(documents),
            'total_characters': total_chars,
            'file_types': file_types,
            'unique_files': len(source_files),
            'source_files': list(source_files)
        }