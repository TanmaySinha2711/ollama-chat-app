"""
Configuration settings for the Ollama Chat App
"""

class Config:
    # Chat related settings
    MAX_CHATS = 5  # Maximum number of chats allowed
    RECENT_CHATS_DISPLAY = 5  # Number of chats to display in sidebar
    
    # Message history settings
    MAX_MESSAGES_BEFORE_SUMMARY = 10  # Number of messages before creating a summary
    RECENT_MESSAGES_AFTER_SUMMARY = 5  # Number of recent messages to keep after summary
    
    # Title generation settings
    MAX_TITLE_LENGTH = 40  # Maximum length of generated chat titles
    DEFAULT_TITLE = "New Chat"  # Default title for new chats
    
    # Model settings
    DEFAULT_MODEL = "deepseek-coder-v2:16b"  # Default model to use
    SYSTEM_MESSAGE = "You are a helpful AI assistant specialized in coding and software development."