#!/usr/bin/env python3
"""
Setup script for the Documentation Chatbot.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("📚 Team Documentation Q&A Chatbot Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version check passed: {sys.version.split()[0]}")

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    directories = [
        "documents",
        "chroma_db",
        "sample_docs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}/")
    
    print("✅ Directories created successfully!")

def setup_environment():
    """Set up environment configuration."""
    print("\n⚙️ Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env and add your OpenAI API key!")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ No .env.example file found")

def create_sample_documents():
    """Create sample documents if they don't exist."""
    print("\n📄 Setting up sample documents...")
    
    # The team_handbook.md was already created, so we just need to move it
    sample_docs_dir = Path("sample_docs")
    documents_dir = Path("documents")
    
    # Copy sample documents to the documents directory
    if sample_docs_dir.exists():
        for file_path in sample_docs_dir.glob("*.md"):
            target_path = documents_dir / file_path.name
            if not target_path.exists():
                shutil.copy(file_path, target_path)
                print(f"   Copied: {file_path.name}")
    
    print("✅ Sample documents set up!")

def run_quick_test():
    """Run a quick test to verify the setup."""
    print("\n🧪 Running quick setup test...")
    
    try:
        # Test imports
        from config import Config
        from chatbot import DocumentationChatbot
        print("✅ All modules can be imported successfully!")
        
        # Check if .env has OpenAI key
        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here":
            print("⚠️  Warning: OpenAI API key not configured in .env file")
            return False
        else:
            print("✅ OpenAI API key found in configuration")
            return True
            
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def print_next_steps(api_key_configured):
    """Print next steps for the user."""
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("-" * 40)
    
    if not api_key_configured:
        print("1. Edit .env file and add your OpenAI API key:")
        print("   OPENAI_API_KEY=your_actual_api_key_here")
        print()
    
    print("2. Add your documentation files to the documents/ directory")
    print()
    print("3. Run the chatbot:")
    print("   Web Interface:    streamlit run streamlit_app.py")
    print("   Command Line:     python cli_app.py")
    print()
    print("4. Example commands:")
    print("   Load documents:   python cli_app.py --load-docs ./documents")
    print("   Ask a question:   python cli_app.py -q 'What is our git workflow?'")
    print()
    print("📚 See README.md for detailed documentation")

def main():
    """Main setup function."""
    print_banner()
    
    # Run setup steps
    check_python_version()
    install_dependencies()
    create_directories()
    setup_environment()
    create_sample_documents()
    api_key_configured = run_quick_test()
    
    # Print completion message
    print_next_steps(api_key_configured)

if __name__ == "__main__":
    main()