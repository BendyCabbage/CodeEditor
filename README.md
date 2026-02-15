# CodeEditor

A collaborative online code editor with real-time synchronization. Built with Flask, React, PostgreSQL, and WebSockets.

## Tech Stack

- **Backend**: Flask, Flask-SocketIO, PostgreSQL, psycopg2
- **Frontend**: React, Monaco Editor
- **Real-time**: WebSockets via Socket.IO

## Prerequisites

- Python 3.x
- Node.js and npm
- PostgreSQL

## Setup (macOS)

### 1. Install PostgreSQL

```bash
brew install postgresql@15
brew services start postgresql@15
```

Add PostgreSQL to your PATH (add to `~/.zshrc` or `~/.bash_profile`):

```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

Reload your shell or run `source ~/.zshrc`.

### 2. Create Database, User, and Table

Create a user (replace `your_username` and `your_password` with your preferred credentials):

```bash
psql postgres -c "CREATE USER your_username WITH PASSWORD 'your_password';"
```

Create the database:

```bash
psql postgres -c "CREATE DATABASE code_editor OWNER your_username;"
```

Create the table:

```bash
psql code_editor -c "CREATE TABLE pages (id VARCHAR(8) PRIMARY KEY, content TEXT);"
```

Grant privileges:

```bash
psql code_editor -c "GRANT ALL PRIVILEGES ON TABLE pages TO your_username;"
```

**Note**: On a fresh Homebrew install, you can skip the user creation and use your macOS username with an empty password instead.

### 3. Configure Environment Variables

Create a `.env` file in `backend/server/`:

```bash
touch backend/server/.env
```

Add your PostgreSQL credentials (use the values from step 2):

```
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
```

**Note**: If using your macOS username with no password, set `SQL_PASSWORD=` (empty value).

### 4. Backend Setup

Create and activate a virtual environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 5. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
python3 server/app.py
```

The backend runs on `http://localhost:5000`.

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm start
```

The frontend runs on `http://localhost:3000`.

## Project Structure

```
CodeEditor/
├── backend/
│   ├── server/
│   │   ├── app.py        # Flask application and WebSocket handlers
│   │   ├── cache.py      # LRU cache implementation
│   │   └── .env          # Environment variables (create this)
│   ├── requirements.txt  # Python dependencies
│   └── venv/             # Virtual environment
└── frontend/
    ├── src/              # React source files
    └── package.json      # Node.js dependencies
```
