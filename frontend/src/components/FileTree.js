import React, { useState, memo } from 'react';
import '../style/file-tree.css';

const FileIcon = ({ extension }) => {
    const iconMap = {
        js: '📜',
        jsx: '⚛️',
        ts: '📘',
        tsx: '⚛️',
        py: '🐍',
        html: '🌐',
        css: '🎨',
        scss: '🎨',
        json: '📋',
        md: '📝',
        svg: '🖼️',
        png: '🖼️',
        jpg: '🖼️',
        gif: '🖼️',
        gitignore: '👁️',
        env: '🔐',
        lock: '🔒',
    };
    
    return <span className="file-icon">{iconMap[extension] || '📄'}</span>;
};

const FolderIcon = ({ isOpen }) => (
    <span className="folder-icon">{isOpen ? '📂' : '📁'}</span>
);

const TreeNode = memo(({ node, onFileSelect, selectedPath, depth = 0 }) => {
    const [isOpen, setIsOpen] = useState(depth < 2);
    
    if (node.type === 'file') {
        const isSelected = selectedPath === node.path;
        return (
            <div 
                className={`tree-item file ${isSelected ? 'selected' : ''}`}
                style={{ paddingLeft: `${depth * 16 + 8}px` }}
                onClick={() => onFileSelect(node)}
            >
                <FileIcon extension={node.extension} />
                <span className="item-name">{node.name}</span>
            </div>
        );
    }
    
    const hasChildren = node.children && node.children.length > 0;
    
    return (
        <div className="tree-node">
            <div 
                className={`tree-item directory ${isOpen ? 'open' : ''}`}
                style={{ paddingLeft: `${depth * 16 + 8}px` }}
                onClick={() => setIsOpen(!isOpen)}
            >
                <span className={`chevron ${isOpen ? 'open' : ''}`}>
                    {hasChildren ? '▶' : ''}
                </span>
                <FolderIcon isOpen={isOpen} />
                <span className="item-name">{node.name || 'root'}</span>
            </div>
            
            {isOpen && hasChildren && (
                <div className="tree-children">
                    {node.children.map((child, index) => (
                        <TreeNode 
                            key={child.path || index}
                            node={child}
                            onFileSelect={onFileSelect}
                            selectedPath={selectedPath}
                            depth={depth + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
});

const FileTree = ({ tree, onFileSelect, selectedPath, projectName, isLoading }) => {
    if (isLoading) {
        return (
            <div className="file-tree loading">
                <div className="tree-header">
                    <span className="project-name">Loading...</span>
                </div>
                <div className="loading-skeleton">
                    {[1,2,3,4,5].map(i => (
                        <div key={i} className="skeleton-item" style={{ width: `${60 + Math.random() * 40}%` }} />
                    ))}
                </div>
            </div>
        );
    }
    
    if (!tree) {
        return (
            <div className="file-tree empty">
                <div className="tree-header">
                    <span className="project-name">{projectName || 'Project'}</span>
                </div>
                <div className="empty-state">
                    <p>No files yet</p>
                </div>
            </div>
        );
    }
    
    return (
        <div className="file-tree">
            <div className="tree-header">
                <span className="project-name">{projectName || 'Project'}</span>
            </div>
            <div className="tree-content">
                {tree.children && tree.children.map((node, index) => (
                    <TreeNode 
                        key={node.path || index}
                        node={node}
                        onFileSelect={onFileSelect}
                        selectedPath={selectedPath}
                    />
                ))}
            </div>
        </div>
    );
};

export default FileTree;

