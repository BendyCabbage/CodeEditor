import os
from pathlib import Path
from typing import Optional

PROJECTS_DIR = Path(__file__).parent.parent / "projects"

PROJECTS_DIR.mkdir(exist_ok=True)

IGNORED_PATTERNS = {'.git', 'node_modules', '__pycache__', '.DS_Store', '.env'}

def get_project_path(project_id: str) -> Path:
    return PROJECTS_DIR / project_id

def project_exists(project_id: str) -> bool:
    return get_project_path(project_id).exists()

def create_project_directory(project_id: str) -> Path:
    project_path = get_project_path(project_id)
    project_path.mkdir(parents=True, exist_ok=True)
    return project_path

def delete_project_directory(project_id: str) -> bool:
    import shutil
    project_path = get_project_path(project_id)
    if project_path.exists():
        shutil.rmtree(project_path)
        return True
    return False

def get_file_tree(project_id: str, relative_path: str = "") -> Optional[dict]:
    project_path = get_project_path(project_id)
    target_path = project_path / relative_path if relative_path else project_path
    
    if not target_path.exists():
        return None
    
    return _build_tree(target_path, project_path)

def _build_tree(path: Path, root: Path) -> dict:
    relative = path.relative_to(root)
    name = path.name or str(relative)
    
    if path.is_file():
        return {
            "name": name,
            "path": str(relative),
            "type": "file",
            "extension": path.suffix[1:] if path.suffix else ""
        }
    
    children = []
    try:
        for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            if child.name in IGNORED_PATTERNS:
                continue
            children.append(_build_tree(child, root))
    except PermissionError:
        pass
    
    return {
        "name": name if name != "." else "",
        "path": str(relative) if str(relative) != "." else "",
        "type": "directory",
        "children": children
    }

def get_file_content(project_id: str, file_path: str) -> Optional[str]:
    project_path = get_project_path(project_id)
    full_path = project_path / file_path
    
    if not full_path.exists() or not full_path.is_file():
        return None
    
    normalized = full_path.resolve()
    if not str(normalized).startswith(str(project_path.resolve())):
        return None
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (UnicodeDecodeError, IOError):
        return None

def save_file_content(project_id: str, file_path: str, content: str) -> bool:
    project_path = get_project_path(project_id)
    full_path = project_path / file_path
    
    normalized = full_path.resolve()
    if not str(normalized).startswith(str(project_path.resolve())):
        return False
    
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError:
        return False

def create_file(project_id: str, file_path: str) -> bool:
    return save_file_content(project_id, file_path, "")

def create_directory(project_id: str, dir_path: str) -> bool:
    project_path = get_project_path(project_id)
    full_path = project_path / dir_path
    
    normalized = full_path.resolve()
    if not str(normalized).startswith(str(project_path.resolve())):
        return False
    
    try:
        full_path.mkdir(parents=True, exist_ok=True)
        return True
    except IOError:
        return False

def delete_file(project_id: str, file_path: str) -> bool:
    import shutil
    project_path = get_project_path(project_id)
    full_path = project_path / file_path
    
    normalized = full_path.resolve()
    if not str(normalized).startswith(str(project_path.resolve())):
        return False
    
    if not full_path.exists():
        return False
    
    try:
        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        return True
    except IOError:
        return False

def rename_file(project_id: str, old_path: str, new_path: str) -> bool:
    project_path = get_project_path(project_id)
    old_full = project_path / old_path
    new_full = project_path / new_path
    
    old_normalized = old_full.resolve()
    new_normalized = new_full.resolve()
    project_resolved = project_path.resolve()
    
    if not str(old_normalized).startswith(str(project_resolved)):
        return False
    if not str(new_normalized).startswith(str(project_resolved)):
        return False
    
    if not old_full.exists():
        return False
    
    try:
        new_full.parent.mkdir(parents=True, exist_ok=True)
        old_full.rename(new_full)
        return True
    except IOError:
        return False

def get_language_from_extension(extension: str) -> str:
    extension_map = {
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'py': 'python',
        'rb': 'ruby',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'go': 'go',
        'rs': 'rust',
        'php': 'php',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'json': 'json',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
        'md': 'markdown',
        'sql': 'sql',
        'sh': 'shell',
        'bash': 'shell',
        'zsh': 'shell',
        'dockerfile': 'dockerfile',
        'vue': 'vue',
        'svelte': 'svelte',
    }
    return extension_map.get(extension.lower(), 'plaintext')

