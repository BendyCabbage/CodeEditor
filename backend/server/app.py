import eventlet
eventlet.monkey_patch()

import random
import string
import re

from flask import Flask, jsonify, redirect, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

from psycopg2 import pool
from cache import LRUCache
from dotenv import load_dotenv
import os

import atexit
import signal

import file_service
import git_service

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

def generate_project_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def is_valid_project_id(project_id) -> bool:
    pattern = '^[a-zA-Z0-9]{12}$'
    return re.match(pattern, project_id) is not None

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

# Project Routes

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json() or {}
    name = data.get('name', 'Untitled Project')
    
    project_id = generate_project_id()
    
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, is_temporary) VALUES (%s, %s, %s);",
            (project_id, name, True)
        )
        conn.commit()
    finally:
        conn_pool.putconn(conn)
    
    file_service.create_project_directory(project_id)
    
    return jsonify({'id': project_id, 'name': name}), 201

@app.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    if not is_valid_project_id(project_id):
        return jsonify({'error': 'Invalid project ID'}), 400
    
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, github_url, created_at, last_accessed, is_temporary FROM projects WHERE id = %s;",
            (project_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Project not found'}), 404
        
        cursor.execute(
            "UPDATE projects SET last_accessed = CURRENT_TIMESTAMP WHERE id = %s;",
            (project_id,)
        )
        conn.commit()
        
        return jsonify({
            'id': result[0],
            'name': result[1],
            'github_url': result[2],
            'created_at': result[3].isoformat() if result[3] else None,
            'last_accessed': result[4].isoformat() if result[4] else None,
            'is_temporary': result[5],
            'is_git_repo': git_service.is_git_repo(project_id),
            'branch': git_service.get_current_branch(project_id)
        })
    finally:
        conn_pool.putconn(conn)

@app.route('/projects/<project_id>/tree', methods=['GET'])
def get_project_tree(project_id):
    if not is_valid_project_id(project_id):
        return jsonify({'error': 'Invalid project ID'}), 400
    
    tree = file_service.get_file_tree(project_id)
    if tree is None:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify(tree)

@app.route('/projects/<project_id>/files/<path:file_path>', methods=['GET'])
def get_file(project_id, file_path):
    if not is_valid_project_id(project_id):
        return jsonify({'error': 'Invalid project ID'}), 400
    
    content = file_service.get_file_content(project_id, file_path)
    if content is None:
        return jsonify({'error': 'File not found'}), 404
    
    extension = file_path.split('.')[-1] if '.' in file_path else ''
    language = file_service.get_language_from_extension(extension)
    
    return jsonify({
        'path': file_path,
        'content': content,
        'language': language
    })

@app.route('/projects/<project_id>/files/<path:file_path>', methods=['PUT'])
def save_file(project_id, file_path):
    if not is_valid_project_id(project_id):
        return jsonify({'error': 'Invalid project ID'}), 400
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content required'}), 400
    
    success = file_service.save_file_content(project_id, file_path, data['content'])
    if not success:
        return jsonify({'error': 'Failed to save file'}), 500
    
    return jsonify({'success': True, 'path': file_path})

@app.route('/projects/<project_id>/files/<path:file_path>', methods=['DELETE'])
def delete_file_route(project_id, file_path):
    if not is_valid_project_id(project_id):
        return jsonify({'error': 'Invalid project ID'}), 400
    
    success = file_service.delete_file(project_id, file_path)
    if not success:
        return jsonify({'error': 'Failed to delete file'}), 500
    
    return jsonify({'success': True})

@app.route('/projects/<project_id>/files', methods=['POST'])
def create_file_route(project_id):
    if not is_valid_project_id(project_id):
        return jsonify({'error': 'Invalid project ID'}), 400
    
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({'error': 'Path required'}), 400
    
    file_path = data['path']
    is_directory = data.get('is_directory', False)
    
    if is_directory:
        success = file_service.create_directory(project_id, file_path)
    else:
        success = file_service.create_file(project_id, file_path)
    
    if not success:
        return jsonify({'error': 'Failed to create file/directory'}), 500
    
    return jsonify({'success': True, 'path': file_path}), 201

@app.route('/projects/clone', methods=['POST'])
def clone_project():
    data = request.get_json()
    if not data or 'github_url' not in data:
        return jsonify({'error': 'GitHub URL required'}), 400
    
    github_url = data['github_url']
    
    repo_name = git_service.get_repo_name_from_url(github_url)
    if not repo_name:
        return jsonify({'error': 'Invalid GitHub URL'}), 400
    
    project_id = generate_project_id()
    name = data.get('name', repo_name)
    
    success, message = git_service.clone_repository(project_id, github_url)
    if not success:
        return jsonify({'error': message}), 500
    
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, github_url, is_temporary) VALUES (%s, %s, %s, %s);",
            (project_id, name, github_url, True)
        )
        conn.commit()
    finally:
        conn_pool.putconn(conn)
    
    return jsonify({
        'id': project_id,
        'name': name,
        'github_url': github_url,
        'message': message
    }), 201

# SocketIO handlers for legacy pages
@socketio.on('code_edit')
def handle_code_edit(data):
    """Handle real-time code edits and update the cache."""
    page_id = data['id']
    new_content = data['content']

    cache.set(page_id, new_content)

    emit('code_update', data, broadcast=True)

# SocketIO handlers for projects
@socketio.on('join_project')
def handle_join_project(data):
    project_id = data.get('project_id')
    if project_id and is_valid_project_id(project_id):
        join_room(f"project_{project_id}")
        emit('joined_project', {'project_id': project_id})

@socketio.on('leave_project')
def handle_leave_project(data):
    project_id = data.get('project_id')
    if project_id:
        leave_room(f"project_{project_id}")

@socketio.on('file_edit')
def handle_file_edit(data):
    project_id = data.get('project_id')
    file_path = data.get('file_path')
    content = data.get('content')
    
    if not project_id or not file_path:
        return
    
    cache_key = f"{project_id}:{file_path}"
    cache.set(cache_key, content)
    
    emit('file_update', data, room=f"project_{project_id}", include_self=False)

@socketio.on('file_cursor')
def handle_file_cursor(data):
    project_id = data.get('project_id')
    if project_id:
        emit('cursor_update', data, room=f"project_{project_id}", include_self=False)

# Sync Cache with DB/Filesystem periodically
def sync_cache_with_db():
    """Periodically sync cache with the database and filesystem."""
    print("Syncing cache with database/filesystem")
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        for key in cache.get_all_keys():
            content = cache.get(key)
            if ':' in key:
                project_id, file_path = key.split(':', 1)
                file_service.save_file_content(project_id, file_path, content)
            else:
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
