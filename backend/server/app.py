import eventlet
eventlet.monkey_patch()

import random
import string
import re

from flask import Flask, jsonify, redirect
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from psycopg2 import pool
from cache import LRUCache
from dotenv import load_dotenv
import os

import atexit
import signal

# Initialize Flask, SocketIO, Redis, and DB connection pool

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

cache = LRUCache(100)

load_dotenv()

# PostgreSQL connection pool
conn_pool = pool.SimpleConnectionPool(1, 20, host="localhost", database="code_editor", user=os.getenv("SQL_USERNAME"), password=os.getenv("SQL_PASSWORD"))

# Utility to generate a unique 8-character ID
def generate_page_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Flask Routes
'''
@app.route('/dashboard')
def dashboard():
    """Serve the dashboard."""
    return render_template('dashboard.html')  # React dashboard will be rendered
'''

@app.route('/new-page', methods=['GET'])
def new_page():
    """Create a new page with a unique ID."""
    page_id = generate_page_id()

    # Create a blank entry in the database
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pages (id, content) VALUES (%s, %s);", (page_id, ""))
        conn.commit()
    finally:
        conn_pool.putconn(conn)

    # Redirect to the new page URL
    return redirect(f'/pages/{page_id}')

def isValidPageId(pageId) -> bool:
    pattern = '^[a-zA-Z0-9]{8}$'
    return re.match(pattern, pageId)

@app.route('/pages/<page_id>', methods=['GET'])
def load_page(page_id):
    if (not isValidPageId(page_id)):
        return jsonify({'error': 'Invalid page ID'}), 400

    """Load a page by ID, using cache if available."""
    # Check cache first
    cached_content = cache.get(page_id)
    if cached_content is not None:
        return jsonify({'id': page_id, 'content': cached_content})

    # Load from DB if not in cache
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM pages WHERE id = %s;", (page_id,))
        result = cursor.fetchone()
        if result:
            content = result[0]
            # Cache the content for future requests
            cache.set(page_id, content)
            return jsonify({'id': page_id, 'content': content})
        else:
            return jsonify({'error': 'Page not found'}), 404
    finally:
        conn_pool.putconn(conn)

# SocketIO handlers
@socketio.on('code_edit')
def handle_code_edit(data):
    """Handle real-time code edits and update the cache."""
    page_id = data['id']
    new_content = data['content']

    # Update the cache with the new content
    cache.set(page_id, new_content)

    # Broadcast the update to all other clients
    emit('code_update', data, broadcast=True)

# Sync Cache with DB periodically
def sync_cache_with_db():
    """Periodically sync cache with the database."""
    print("Syncing cache with database")
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        for key in cache.get_all_keys():
            content = cache.get(key)
            cursor.execute("UPDATE pages SET content = %s WHERE id = %s;", (content, key))
        conn.commit()
    finally:
        conn_pool.putconn(conn)

# Handling server shutdown
def on_server_shutdown():
    """Sync cache with DB during shutdown."""
    print("Shutting down... Syncing cache with the database.")
    sync_cache_with_db()
    cache.clear()

def handle_signal(signum, frame):
    print(f"Received signal {signum}. Syncing cache and shutting down.")
    sync_cache_with_db()
    cache.clear()
    exit(0)

atexit.register(on_server_shutdown)
signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_signal)  # Termination

# Schedule cache sync every 30 seconds
eventlet.spawn_after(30, sync_cache_with_db)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
