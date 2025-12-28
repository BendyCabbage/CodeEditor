-- Projects table for storing project metadata
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(12) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    github_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_temporary BOOLEAN DEFAULT TRUE
);

-- Index for faster lookups on temporary projects (for cleanup)
CREATE INDEX IF NOT EXISTS idx_projects_temporary ON projects(is_temporary, last_accessed);

