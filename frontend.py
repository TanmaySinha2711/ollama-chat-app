import streamlit as st
from backend import ChatBackend
import re
import os

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "title_generated" not in st.session_state:
        st.session_state.title_generated = False

def handle_new_chat(chat_backend):
    total_chats = len(chat_backend.get_all_chats())  # Get total number of chats
    if total_chats >= 5:
        chat_backend.delete_oldest_chat()
    
    st.session_state.current_chat_id = chat_backend.create_new_chat()
    st.session_state.messages = []
    st.session_state.title_generated = False
    st.rerun()

def handle_chat_selection(chat_id, chat_backend):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = chat_backend.get_chat_history(chat_id)
    st.session_state.title_generated = True
    st.rerun()

def handle_chat_deletion(chat_id, chat_backend):
    chat_backend.delete_chat(chat_id)
    if st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = None
        st.session_state.messages = []
        st.session_state.title_generated = False
    st.rerun()

def render_sidebar(chat_backend):
    with st.sidebar:
        # Improved New Chat button with icon
        st.button("➕ New Chat", key="new_chat", use_container_width=True, type="primary")
        
        st.write("Recent Chats:")
        recent_chats = chat_backend.get_recent_chats()
        
        # Display chats with rename and delete options
        for chat_id, title, created_at, last_updated in recent_chats:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                if st.button(f"{title}", key=f"chat_{chat_id}"):
                    handle_chat_selection(chat_id, chat_backend)
            
            with col2:
                if st.button("✏️", key=f"rename_{chat_id}"):
                    st.session_state.renaming_chat = chat_id
                    st.session_state.current_title = title
            
            with col3:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    handle_chat_deletion(chat_id, chat_backend)
            
            # Show rename input field if this chat is being renamed
            if st.session_state.get('renaming_chat') == chat_id:
                new_title = st.text_input(
                    "New title",
                    value=st.session_state.current_title,
                    key=f"new_title_{chat_id}"
                )
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Save", key=f"save_{chat_id}"):
                        chat_backend.update_chat_title(chat_id, new_title)
                        st.session_state.renaming_chat = None
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_{chat_id}"):
                        st.session_state.renaming_chat = None
                        st.rerun()

def handle_chat_response(prompt, chat_backend):
    # Create message with chat_id
    message = {
        "role": "user",
        "content": prompt,
        "chat_id": st.session_state.current_chat_id
    }

    # Add user message to session state and database immediately
    st.session_state.messages.append(message)
    chat_backend.save_message(st.session_state.current_chat_id, "user", prompt)

    # Get document context if available
    doc_context = st.session_state.get('uploaded_doc_text', '')

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare for assistant response streaming
    with st.chat_message("assistant"):
        # Use st.empty() to create a container we can update in place
        message_placeholder = st.empty()
        full_response = ""
        
        # Disable input and show stop button (requires frontend logic outside this function)
        # For now, we'll just simulate the streaming display

        try:
            # Pass messages and doc_context to backend, which now streams
            # We pass the latest message in a list as expected by the backend function signature
            for chunk in chat_backend.get_response([message], doc_context=doc_context):
                full_response += chunk
                # Update the message container with the current full response
                message_placeholder.markdown(full_response + "▌") # Add a blinking cursor effect
            
            # Remove the cursor after streaming finishes
            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"Error: {str(e)}"
            message_placeholder.error(full_response) # Display error in the placeholder

        # Add the complete response to session state and database after streaming finishes
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        chat_backend.save_message(st.session_state.current_chat_id, "assistant", full_response)

        # Re-enable input and hide stop button (requires frontend logic outside this function)

        # Generate title if it hasn't been generated
        if not st.session_state.title_generated:
            # Use the original prompt for title generation
            title = chat_backend.generate_chat_title(prompt)
            chat_backend.update_chat_title(st.session_state.current_chat_id, title)
            st.session_state.title_generated = True
            # st.rerun() # Avoid rerunning here to prevent interrupting the stream display

def main():
    st.title("Chat with Deepseek Coder")

    chat_backend = ChatBackend()
    initialize_session_state()

    render_sidebar(chat_backend)

    # Add file uploader
    uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'doc', 'docx'])
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        # Determine file type, mapping 'plain' to 'txt'
        file_type_raw = uploaded_file.type.split('/')[-1]
        file_type = 'txt' if file_type_raw == 'plain' else file_type_raw

        # Save file to disk for processing
        file_path = f"uploaded_files/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        # Process document
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        try:
            extracted_text, vector_store_path = processor.process_document(file_path, file_type)
            st.session_state['uploaded_doc_text'] = extracted_text
            st.session_state['vector_store_path'] = vector_store_path
            st.success(f"File {uploaded_file.name} uploaded and processed successfully!")
        except Exception as e:
            st.error(f"Failed to process file: {e}")
        # Save document info to DB (optional, depending on whether you want to link messages to documents)
        # document_id = chat_backend.save_document(uploaded_file.name, file_content, file_type)
        # st.success(f"File {uploaded_file.name} uploaded successfully!")

    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = chat_backend.create_new_chat()
        st.session_state.messages = []
        st.session_state.title_generated = False

    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input area
    # We need to manage the disabled state here based on whether streaming is active
    # For simplicity in this code block, we'll just add a placeholder comment
    # You would typically use st.session_state to track if streaming is ongoing
    prompt = st.chat_input("What would you like to ask?") # Add disabled=st.session_state.streaming_active

    if prompt:
        # Set a session state flag to indicate streaming is active
        # st.session_state.streaming_active = True # Add this
        handle_chat_response(prompt, chat_backend)
        # st.session_state.streaming_active = False # Reset this after streaming finishes

if __name__ == "__main__":
    if not os.path.exists("uploaded_files"):
        os.makedirs("uploaded_files")
    main()