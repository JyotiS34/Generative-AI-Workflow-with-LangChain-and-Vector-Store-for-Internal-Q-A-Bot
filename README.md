# 📚 Team Documentation Q&A Chatbot

A powerful AI-powered chatbot for answering questions about your team's internal documentation using LangChain, Chroma/FAISS, and OpenAI.

## ✨ Features

- **Multi-format Document Support**: PDF, DOCX, DOC, TXT, and Markdown files
- **Vector Database Options**: Choose between Chroma or FAISS for vector storage
- **Smart Document Chunking**: Optimized text splitting for better retrieval
- **Source Attribution**: See which documents the answers come from
- **Multiple Interfaces**: Web UI (Streamlit) and Command Line Interface
- **Conversation Memory**: Context-aware conversations
- **Real-time Document Upload**: Add new documents on the fly
- **Advanced Search**: Search through documents without generating answers

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd documentation-chatbot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Add Documents

Create a `documents` directory and add your documentation files:

```bash
mkdir documents
# Copy your PDF, DOCX, TXT, or MD files to this directory
```

### 4. Run the Application

#### Web Interface (Recommended)

```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501`

#### Command Line Interface

```bash
# Interactive mode
python cli_app.py

# Load documents and ask a question
python cli_app.py --load-docs ./documents --question "How do I deploy the application?"

# Just ask a question (if documents already loaded)
python cli_app.py -q "What is our coding style guide?"
```

## 🔧 Configuration Options

All configuration is done through environment variables in the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `VECTOR_DB_TYPE` | `chroma` | Vector database (`chroma` or `faiss`) |
| `CHROMA_PERSIST_DIRECTORY` | `./chroma_db` | Chroma database directory |
| `FAISS_INDEX_PATH` | `./faiss_index` | FAISS index file path |
| `DOCS_DIRECTORY` | `./documents` | Default documents directory |
| `CHUNK_SIZE` | `1000` | Document chunk size for processing |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Number of documents to retrieve |
| `SIMILARITY_THRESHOLD` | `0.7` | Similarity threshold for retrieval |
| `MAX_TOKENS` | `1000` | Maximum tokens in response |
| `TEMPERATURE` | `0.7` | LLM temperature (0-1) |

## 💻 Usage Examples

### Web Interface

1. **Upload Documents**: Use the sidebar to upload files or load from a directory
2. **Ask Questions**: Type questions in the chat interface
3. **View Sources**: Expand the sources section to see supporting documents
4. **Advanced Search**: Use the search feature to find specific content

### Command Line Interface

```bash
# Interactive session
python cli_app.py --interactive

# Load documents from a specific directory
python cli_app.py --load-docs /path/to/your/docs

# Ask a single question
python cli_app.py -q "How do I configure the database?"

# Use FAISS instead of Chroma
python cli_app.py --db-type faiss

# Get help
python cli_app.py --help
```

### Programmatic Usage

```python
from chatbot import DocumentationChatbot

# Initialize chatbot
chatbot = DocumentationChatbot()

# Load documents
result = chatbot.load_documents("./documents")
print(result)

# Ask a question
response = chatbot.ask_question("How do I deploy the application?")
print(response["answer"])

# Search documents
results = chatbot.search_documents("deployment process", k=3)
for result in results:
    print(f"Score: {result['similarity_score']}")
    print(f"Content: {result['content'][:100]}...")
```

## 🏗️ Architecture

The chatbot consists of several key components:

- **`config.py`**: Configuration management
- **`document_processor.py`**: Document loading and chunking
- **`vector_db.py`**: Vector database abstraction (Chroma/FAISS)
- **`chatbot.py`**: Main chatbot logic using LangChain
- **`streamlit_app.py`**: Web interface
- **`cli_app.py`**: Command-line interface

### Data Flow

1. **Document Ingestion**: Documents are loaded and split into chunks
2. **Embedding Generation**: OpenAI embeddings are created for each chunk
3. **Vector Storage**: Embeddings are stored in Chroma or FAISS
4. **Query Processing**: User questions are embedded and matched against stored vectors
5. **Context Retrieval**: Relevant document chunks are retrieved
6. **Answer Generation**: OpenAI generates answers based on retrieved context

## 🔄 Vector Database Comparison

| Feature | Chroma | FAISS |
|---------|---------|--------|
| **Persistence** | Built-in | Manual save/load |
| **Scalability** | Good | Excellent |
| **Memory Usage** | Higher | Lower |
| **Setup Complexity** | Easier | More complex |
| **Performance** | Good | Faster |

**Recommendation**: Use Chroma for development and small teams, FAISS for production and large document sets.

## 🛠️ Advanced Usage

### Custom Document Processing

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()

# Process a single document
documents = processor.load_single_document("path/to/doc.pdf")

# Get statistics
stats = processor.get_document_stats(documents)
print(stats)
```

### Custom Vector Database

```python
from vector_db import VectorDBManager

# Initialize with specific database type
db_manager = VectorDBManager(db_type="faiss")

# Add documents
db_manager.add_documents(documents)

# Search
results = db_manager.search("query", k=5, with_scores=True)
```

## 🐛 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY environment variable is required"**
   - Ensure you've set your OpenAI API key in the `.env` file

2. **"No documents found to load"**
   - Check that your documents directory exists and contains supported files
   - Supported formats: PDF, DOCX, DOC, TXT, MD

3. **"Failed to initialize chatbot"**
   - Verify your OpenAI API key is valid
   - Check your internet connection
   - Ensure all dependencies are installed

4. **Slow performance**
   - Consider using FAISS instead of Chroma
   - Reduce chunk size if processing large documents
   - Use a faster OpenAI model like `gpt-3.5-turbo`

### Performance Tips

- **Document Size**: Keep individual documents under 10MB for optimal processing
- **Chunk Size**: Experiment with chunk sizes (500-2000) based on your content
- **Retrieval K**: Start with 3-5 retrieved documents, adjust based on results
- **Model Choice**: Use `gpt-4` for better accuracy, `gpt-3.5-turbo` for speed

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the configuration options
3. Check the logs for detailed error messages
4. Open an issue in the repository

## 🔮 Future Enhancements

- [ ] Support for more document formats (PowerPoint, Excel, etc.)
- [ ] Web scraping capabilities for online documentation
- [ ] Integration with popular documentation platforms (Confluence, Notion, etc.)
- [ ] Multi-language support
- [ ] Document versioning and update tracking
- [ ] Analytics and usage metrics
- [ ] API endpoints for integration with other tools
- [ ] Docker containerization
- [ ] Authentication and user management