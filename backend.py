from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.summarize import load_summarize_chain
from db_manager import DatabaseManager

class ChatBackend:
    def __init__(self):
        self.model = ChatOllama(model="deepseek-coder-v2:16b")
        self.db = DatabaseManager()
        self.chat_histories = {}  # Store chat histories by chat_id
        
        # Define a consistent system message
        self.system_message = SystemMessage(
            content="You are a helpful AI assistant specialized in coding and software development."
        )

    def _get_or_create_chat_history(self, chat_id):
        if chat_id not in self.chat_histories:
            history = ChatMessageHistory()
            history.add_message(self.system_message)
            self.chat_histories[chat_id] = history
            
            # Load existing messages from database
            messages = self.db.get_chat_history(chat_id)
            
            # If there are too many messages, load the summary instead
            if len(messages) > 10:  # Adjust threshold as needed
                summary = self._get_or_create_summary(chat_id, messages[:10])
                history.add_ai_message(f"Previous conversation summary: {summary}")
                # Add only the most recent messages after summary
                for msg in messages[-5:]:  # Keep last 5 messages
                    if msg['role'] == 'user':
                        history.add_user_message(msg['content'])
                    elif msg['role'] == 'assistant':
                        history.add_ai_message(msg['content'])
            else:
                # Load all messages if under threshold
                for msg in messages:
                    if msg['role'] == 'user':
                        history.add_user_message(msg['content'])
                    elif msg['role'] == 'assistant':
                        history.add_ai_message(msg['content'])
        
        return self.chat_histories[chat_id]

    def _get_or_create_summary(self, chat_id, messages):
        try:
            # Create a summarization chain
            chain = load_summarize_chain(self.model, chain_type="map_reduce")
            
            # Convert messages to documents format
            docs = [
                f"{msg['role']}: {msg['content']}"
                for msg in messages
            ]
            
            # Generate summary
            summary = chain.invoke(docs)
            
            # Store summary in database
            self.db.save_message(chat_id, "summary", summary)
            
            return summary
        except Exception as e:
            print(f"Summarization error: {str(e)}")
            return "Previous conversation summary not available."

    def get_response(self, messages):
        try:
            # Get chat_id from the current chat context
            chat_id = messages[0].get('chat_id') if messages else None
            if not chat_id:
                raise ValueError("Chat ID not provided")
            
            history = self._get_or_create_chat_history(chat_id)
            
            # Get the latest user message
            latest_message = messages[-1]['content']
            
            # Add to history
            history.add_user_message(latest_message)
            
            # Create prompt template with history
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant specialized in coding."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Get response using the chat model
            chain = prompt | self.model
            response = chain.invoke({
                "chat_history": history.messages[1:],  # Exclude system message
                "input": latest_message
            })
            
            # Add response to history
            history.add_ai_message(response.content)
            
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"

    def delete_chat(self, chat_id):
        # Clean up chat history when deleting chat
        if chat_id in self.chat_histories:
            del self.chat_histories[chat_id]
        self.db.delete_chat(chat_id)

    def generate_chat_title(self, first_message):
        try:
            # Use Langchain for title generation with a more structured prompt
            prompt = HumanMessage(
                content="You are a title generator. Generate a very short, concise title (max 40 chars) for this message. Output only the title, no quotes or explanations: " + first_message
            )
            response = self.model.invoke([prompt])
            
            # Clean up the response more thoroughly
            title = response.content.strip().strip('"').strip("'").strip()
            
            # Ensure we have a valid title
            if not title or len(title) > 40:
                title = first_message[:37] + "..."
            
            return title
        except Exception as e:
            print(f"Title generation error: {str(e)}")  # For debugging
            return "New Chat"

    def create_new_chat(self):
        return self.db.create_new_chat()

    def update_chat_title(self, chat_id, title):
        self.db.update_chat_title(chat_id, title)

    def save_message(self, chat_id, role, content):
        self.db.save_message(chat_id, role, content)

    def get_chat_history(self, chat_id):
        return self.db.get_chat_history(chat_id)

    def get_recent_chats(self):
        return self.db.get_recent_chats()

    def delete_chat(self, chat_id):
        self.db.delete_chat(chat_id)

    def delete_oldest_chat(self):
        self.db.delete_oldest_chat()