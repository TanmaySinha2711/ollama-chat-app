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

    # Add message to session state with chat_id
    st.session_state.messages.append(message)
    chat_backend.save_message(st.session_state.current_chat_id, "user", prompt)

    # Get document context if available
    doc_context = st.session_state.get('uploaded_doc_text', '')
    # We will pass doc_context separately, not append to the prompt string here

    with st.chat_message("user"):
        st.markdown(prompt) # Display only the original user prompt

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass messages and doc_context to backend
            response = chat_backend.get_response([message], doc_context=doc_context)

            # Extract code blocks from markdown response
            code_blocks = re.findall(r'```(\w+)?\n(.*?)```', response, re.DOTALL)

            # Display response with download buttons for code blocks
            current_pos = 0
            for idx, match in enumerate(re.finditer(r'```(\w+)?\n(.*?)```', response, re.DOTALL)):
                # Display text before code block
                st.markdown(response[current_pos:match.start()])

                lang = match.group(1) or 'txt'
                code = match.group(2)

                # Create columns for code block and buttons
                col1, col2, col3 = st.columns([10, 1, 1])

                with col1:
                    st.code(code, language=lang)

                with col2:
                    # Simplified copy button without session state
                    st.button("📋", key=f"copy_{idx}", help="Copy code")

                with col3:
                    # Get appropriate file extension
                    extension = {
                        'python': '.py',
                        'javascript': '.js',
                        'typescript': '.ts',
                        'java': '.java',
                        'cpp': '.cpp',
                        'c': '.c',
                        'csharp': '.cs',
                        'go': '.go',
                        'rust': '.rs',
                        'php': '.php',
                        'ruby': '.rb',
                        'swift': '.swift',
                        'kotlin': '.kt',
                        'sql': '.sql',
                        'html': '.html',
                        'css': '.css',
                        'json': '.json',
                        'yaml': '.yml',
                        'xml': '.xml',
                        'markdown': '.md',
                        'shell': '.sh',
                        'bash': '.sh',
                        'powershell': '.ps1',
                        'dockerfile': '.dockerfile',
                    }.get(lang.lower(), '.txt')

                    # Download button with unique key
                    st.download_button(
                        label="⬇️",
                        data=code,
                        file_name=f"chat_response{extension}",
                        mime="text/plain",
                        key=f"download_{idx}",
                        help=f"Download as chat_response{extension}"
                    )

                current_pos = match.end()

            # Display any remaining text after last code block
            if current_pos < len(response):
                st.markdown(response[current_pos:])

            st.session_state.messages.append({"role": "assistant", "content": response})
            chat_backend.save_message(st.session_state.current_chat_id, "assistant", response)

            if not st.session_state.title_generated:
                title = chat_backend.generate_chat_title(prompt) # Use original prompt for title
                chat_backend.update_chat_title(st.session_state.current_chat_id, title)
                st.session_state.title_generated = True
                st.rerun()

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
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("What would you like to ask?"):
        handle_chat_response(prompt, chat_backend)

if __name__ == "__main__":
    if not os.path.exists("uploaded_files"):
        os.makedirs("uploaded_files")
    main()