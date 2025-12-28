import re
from pathlib import Path
from typing import Optional, Tuple
from git import Repo, GitCommandError
from file_service import get_project_path, create_project_directory

def parse_github_url(url: str) -> Optional[Tuple[str, str]]:
    patterns = [
        r'https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url.strip())
        if match:
            return match.group(1), match.group(2)
    
    return None

def normalize_github_url(url: str) -> Optional[str]:
    parsed = parse_github_url(url)
    if not parsed:
        return None
    
    owner, repo = parsed
    return f"https://github.com/{owner}/{repo}.git"

def clone_repository(project_id: str, github_url: str) -> Tuple[bool, str]:
    normalized_url = normalize_github_url(github_url)
    if not normalized_url:
        return False, "Invalid GitHub URL format"
    
    project_path = get_project_path(project_id)
    
    if project_path.exists():
        import shutil
        shutil.rmtree(project_path)
    
    try:
        Repo.clone_from(normalized_url, project_path, depth=1)
        return True, "Repository cloned successfully"
    except GitCommandError as e:
        return False, f"Git clone failed: {str(e)}"
    except Exception as e:
        return False, f"Clone failed: {str(e)}"

def get_repo_name_from_url(github_url: str) -> Optional[str]:
    parsed = parse_github_url(github_url)
    if parsed:
        return parsed[1]
    return None

def is_git_repo(project_id: str) -> bool:
    project_path = get_project_path(project_id)
    git_dir = project_path / ".git"
    return git_dir.exists() and git_dir.is_dir()

def get_repo_status(project_id: str) -> Optional[dict]:
    if not is_git_repo(project_id):
        return None
    
    try:
        repo = Repo(get_project_path(project_id))
        return {
            "branch": repo.active_branch.name if not repo.head.is_detached else "detached",
            "is_dirty": repo.is_dirty(),
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff("HEAD")]
        }
    except Exception:
        return None

def get_current_branch(project_id: str) -> Optional[str]:
    if not is_git_repo(project_id):
        return None
    
    try:
        repo = Repo(get_project_path(project_id))
        if repo.head.is_detached:
            return "detached"
        return repo.active_branch.name
    except Exception:
        return None

