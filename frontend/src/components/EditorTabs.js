import React from 'react';
import '../style/editor-tabs.css';

const getFileName = (path) => {
    if (!path) return 'untitled';
    const parts = path.split('/');
    return parts[parts.length - 1];
};

const TabIcon = ({ extension }) => {
    const colorMap = {
        js: '#f7df1e',
        jsx: '#61dafb',
        ts: '#3178c6',
        tsx: '#61dafb',
        py: '#3776ab',
        html: '#e34f26',
        css: '#1572b6',
        scss: '#cc6699',
        json: '#f5a623',
        md: '#083fa1',
    };
    
    const color = colorMap[extension] || '#808080';
    
    return (
        <span className="tab-icon" style={{ color }}>
            ●
        </span>
    );
};

const EditorTabs = ({ openFiles, activeFile, onTabSelect, onTabClose }) => {
    if (openFiles.length === 0) {
        return null;
    }
    
    return (
        <div className="editor-tabs">
            <div className="tabs-container">
                {openFiles.map((file) => {
                    const isActive = file.path === activeFile;
                    const fileName = getFileName(file.path);
                    const extension = file.path.split('.').pop();
                    
                    return (
                        <div 
                            key={file.path}
                            className={`tab ${isActive ? 'active' : ''} ${file.isDirty ? 'dirty' : ''}`}
                            onClick={() => onTabSelect(file.path)}
                        >
                            <TabIcon extension={extension} />
                            <span className="tab-name">{fileName}</span>
                            {file.isDirty && <span className="dirty-indicator">●</span>}
                            <button 
                                className="close-tab"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onTabClose(file.path);
                                }}
                            >
                                ×
                            </button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default EditorTabs;

