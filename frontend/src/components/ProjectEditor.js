import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Editor } from '@monaco-editor/react';
import io from 'socket.io-client';
import { api } from '../util/sendRequest';
import FileTree from './FileTree';
import EditorTabs from './EditorTabs';
import '../style/project-editor.css';

const socket = io('http://localhost:5000');

const ProjectEditor = () => {
    const { projectId } = useParams();
    const [project, setProject] = useState(null);
    const [tree, setTree] = useState(null);
    const [openFiles, setOpenFiles] = useState([]);
    const [activeFile, setActiveFile] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const editorRef = useRef(null);
    const saveTimeoutRef = useRef({});

    useEffect(() => {
        const loadProject = async () => {
            try {
                const [projectData, treeData] = await Promise.all([
                    api.getProject(projectId),
                    api.getProjectTree(projectId)
                ]);
                
                if (projectData.error) {
                    setError(projectData.error);
                    return;
                }
                
                setProject(projectData);
                setTree(treeData);
            } catch (err) {
                setError('Failed to load project');
            } finally {
                setIsLoading(false);
            }
        };

        loadProject();

        socket.emit('join_project', { project_id: projectId });

        socket.on('file_update', (data) => {
            if (data.project_id === projectId) {
                setOpenFiles(prev => prev.map(f => 
                    f.path === data.file_path 
                        ? { ...f, content: data.content }
                        : f
                ));
            }
        });

        return () => {
            socket.emit('leave_project', { project_id: projectId });
            socket.off('file_update');
            Object.values(saveTimeoutRef.current).forEach(clearTimeout);
        };
    }, [projectId]);

    const handleFileSelect = useCallback(async (node) => {
        if (node.type !== 'file') return;
        
        const existingFile = openFiles.find(f => f.path === node.path);
        if (existingFile) {
            setActiveFile(node.path);
            return;
        }
        
        try {
            const fileData = await api.getFile(projectId, node.path);
            if (fileData.error) {
                console.error('Failed to load file:', fileData.error);
                return;
            }
            
            const newFile = {
                path: node.path,
                content: fileData.content,
                language: fileData.language,
                isDirty: false,
                originalContent: fileData.content
            };
            
            setOpenFiles(prev => [...prev, newFile]);
            setActiveFile(node.path);
        } catch (err) {
            console.error('Error loading file:', err);
        }
    }, [openFiles, projectId]);

    const handleTabSelect = useCallback((path) => {
        setActiveFile(path);
    }, []);

    const handleTabClose = useCallback((path) => {
        setOpenFiles(prev => {
            const filtered = prev.filter(f => f.path !== path);
            if (activeFile === path && filtered.length > 0) {
                setActiveFile(filtered[filtered.length - 1].path);
            } else if (filtered.length === 0) {
                setActiveFile(null);
            }
            return filtered;
        });
        
        if (saveTimeoutRef.current[path]) {
            clearTimeout(saveTimeoutRef.current[path]);
            delete saveTimeoutRef.current[path];
        }
    }, [activeFile]);

    const handleEditorMount = (editor) => {
        editorRef.current = editor;
    };

    const handleEditorChange = useCallback((value) => {
        if (!activeFile) return;
        
        setOpenFiles(prev => prev.map(f => {
            if (f.path === activeFile) {
                return { 
                    ...f, 
                    content: value, 
                    isDirty: value !== f.originalContent 
                };
            }
            return f;
        }));
        
        socket.emit('file_edit', {
            project_id: projectId,
            file_path: activeFile,
            content: value
        });
        
        if (saveTimeoutRef.current[activeFile]) {
            clearTimeout(saveTimeoutRef.current[activeFile]);
        }
        
        saveTimeoutRef.current[activeFile] = setTimeout(async () => {
            const file = openFiles.find(f => f.path === activeFile);
            if (file && file.isDirty) {
                await api.saveFile(projectId, activeFile, value);
                setOpenFiles(prev => prev.map(f => 
                    f.path === activeFile 
                        ? { ...f, isDirty: false, originalContent: value }
                        : f
                ));
            }
        }, 2000);
    }, [activeFile, projectId, openFiles]);

    const activeFileData = openFiles.find(f => f.path === activeFile);

    if (error) {
        return (
            <div className="project-editor error-state">
                <div className="error-content">
                    <h2>Error</h2>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="project-editor">
            <div className="sidebar">
                <FileTree 
                    tree={tree}
                    onFileSelect={handleFileSelect}
                    selectedPath={activeFile}
                    projectName={project?.name}
                    isLoading={isLoading}
                />
            </div>
            
            <div className="main-content">
                <EditorTabs 
                    openFiles={openFiles}
                    activeFile={activeFile}
                    onTabSelect={handleTabSelect}
                    onTabClose={handleTabClose}
                />
                
                <div className="editor-container">
                    {activeFileData ? (
                        <Editor
                            height="100%"
                            language={activeFileData.language}
                            value={activeFileData.content}
                            onChange={handleEditorChange}
                            onMount={handleEditorMount}
                            theme="vs-dark"
                            options={{
                                fontSize: 14,
                                fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
                                minimap: { enabled: true },
                                scrollBeyondLastLine: false,
                                automaticLayout: true,
                                tabSize: 2,
                                wordWrap: 'off',
                                lineNumbers: 'on',
                                renderWhitespace: 'selection',
                                cursorBlinking: 'smooth',
                                cursorSmoothCaretAnimation: 'on',
                            }}
                        />
                    ) : (
                        <div className="no-file-open">
                            <div className="welcome-message">
                                <h2>Welcome to {project?.name || 'your project'}</h2>
                                <p>Select a file from the sidebar to start editing</p>
                                {project?.github_url && (
                                    <div className="git-info">
                                        <span className="branch-badge">
                                            🌿 {project.branch || 'main'}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProjectEditor;

