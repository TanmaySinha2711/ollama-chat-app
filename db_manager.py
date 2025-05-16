import sqlite3
import json
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('chat_history.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP,
                last_updated TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                document_id INTEGER,
                FOREIGN KEY (chat_id) REFERENCES chats (id),
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                content TEXT,
                embedding_path TEXT,
                file_type TEXT,
                uploaded_at TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_new_chat(self, title="New Chat"):
        cursor = self.conn.cursor()
        now = datetime.now()
        cursor.execute(
            'INSERT INTO chats (title, created_at, last_updated) VALUES (?, ?, ?)',
            (title, now, now)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_chat_title(self, chat_id, title):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE chats SET title = ? WHERE id = ?',
            (title, chat_id)
        )
        self.conn.commit()

    def execute_query(self, query, params=None):
        with self.conn:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def save_message(self, chat_id, role, content):
        now = datetime.now()
        self.execute_query(
            'INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
            (chat_id, role, content, now)
        )
        self.execute_query(
            'UPDATE chats SET last_updated = ? WHERE id = ?',
            (now, chat_id)
        )

    def get_chat_history(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp', (chat_id,))
        messages = [{'role': role, 'content': content} for role, content in cursor.fetchall()]
        return messages

    def get_recent_chats(self, limit=None):
        if limit is None:
            limit = Config.RECENT_CHATS_DISPLAY
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, title, created_at, last_updated FROM chats ORDER BY last_updated DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

    def get_all_chats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title, created_at, last_updated FROM chats ORDER BY last_updated DESC')
        return cursor.fetchall()

    def delete_chat(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
        cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
        self.conn.commit()

    def delete_oldest_chat(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM chats ORDER BY last_updated ASC LIMIT 1')
        oldest_chat = cursor.fetchone()
        if oldest_chat:
            self.delete_chat(oldest_chat[0])

    def save_document(self, filename, content, file_type):
        cursor = self.conn.cursor()
        now = datetime.now()
        cursor.execute(
            'INSERT INTO documents (filename, content, file_type, uploaded_at) VALUES (?, ?, ?, ?)',
            (filename, content, file_type, now)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_document(self, document_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
        return cursor.fetchone()

    def save_message_with_document(self, chat_id, role, content, document_id=None):
        now = datetime.now()
        self.execute_query(
            'INSERT INTO messages (chat_id, role, content, timestamp, document_id) VALUES (?, ?, ?, ?, ?)',
            (chat_id, role, content, now, document_id)
        )
        self.execute_query(
            'UPDATE chats SET last_updated = ? WHERE id = ?',
            (now, chat_id)
        )