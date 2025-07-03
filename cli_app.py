#!/usr/bin/env python3
"""
Command-line interface for the Documentation Chatbot.
"""

import argparse
import sys
import os
from typing import Dict, Any

from chatbot import DocumentationChatbot
from config import Config

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("📚 Team Documentation Q&A Chatbot")
    print("=" * 60)
    print()

def print_response(response: Dict[str, Any]):
    """Print the chatbot response in a formatted way."""
    print(f"\n🤖 Answer:")
    print("-" * 40)
    print(response["answer"])
    
    if response.get("sources"):
        print(f"\n📄 Sources ({len(response['sources'])} documents):")
        print("-" * 40)
        for i, source in enumerate(response["sources"]):
            print(f"\nSource {i+1}:")
            print(f"  File: {source['metadata'].get('file_name', 'Unknown')}")
            print(f"  Content: {source['content'][:100]}...")
    print()

def interactive_mode(chatbot: DocumentationChatbot):
    """Run the chatbot in interactive mode."""
    print("🔄 Interactive mode started. Type 'quit' or 'exit' to stop.")
    print("💡 Type 'help' for available commands.")
    print()
    
    while True:
        try:
            user_input = input("❓ You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if user_input.lower() == 'info':
                info = chatbot.get_system_info()
                print("\n📊 System Information:")
                print("-" * 40)
                for key, value in info.items():
                    print(f"  {key}: {value}")
                print()
                continue
            
            if user_input.lower() == 'clear':
                chatbot.reset_conversation()
                print("🧹 Conversation history cleared.")
                continue
            
            if not user_input:
                continue
            
            # Get response from chatbot
            response = chatbot.ask_question(user_input)
            
            if response["status"] == "error":
                print(f"\n❌ Error: {response['message']}")
            else:
                print_response(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def print_help():
    """Print available commands."""
    print("\n📋 Available Commands:")
    print("-" * 40)
    print("  help     - Show this help message")
    print("  info     - Show system information")
    print("  clear    - Clear conversation history")
    print("  quit/exit - Exit the application")
    print("  Or just type your question!")
    print()

def load_documents_command(chatbot: DocumentationChatbot, directory: str):
    """Load documents from a directory."""
    print(f"📁 Loading documents from: {directory}")
    result = chatbot.load_documents(directory)
    
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        if "stats" in result:
            stats = result["stats"]
            print(f"   📊 Total chunks: {stats['total_chunks']}")
            print(f"   📊 Unique files: {stats['unique_files']}")
            print(f"   📊 File types: {stats['file_types']}")
    else:
        print(f"⚠️ {result['message']}")

def ask_question_command(chatbot: DocumentationChatbot, question: str):
    """Ask a single question and exit."""
    response = chatbot.ask_question(question)
    
    if response["status"] == "error":
        print(f"❌ Error: {response['message']}")
        sys.exit(1)
    else:
        print_response(response)

def main():
    """Main CLI application."""
    parser = argparse.ArgumentParser(
        description="Team Documentation Q&A Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Commands
    parser.add_argument(
        "--load-docs", 
        type=str, 
        metavar="DIRECTORY",
        help="Load documents from a directory"
    )
    
    parser.add_argument(
        "--question", "-q",
        type=str,
        help="Ask a single question and exit"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (default if no other command)"
    )
    
    # Configuration options
    parser.add_argument(
        "--db-type",
        type=str,
        choices=["chroma", "faiss"],
        default=None,
        help="Vector database type (default: from config)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    try:
        # Initialize chatbot
        print("🔧 Initializing chatbot...")
        chatbot = DocumentationChatbot(db_type=args.db_type)
        print("✅ Chatbot initialized successfully!")
        
        # Execute commands
        if args.load_docs:
            load_documents_command(chatbot, args.load_docs)
        
        if args.question:
            ask_question_command(chatbot, args.question)
        elif args.interactive or (not args.load_docs and not args.question):
            interactive_mode(chatbot)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()