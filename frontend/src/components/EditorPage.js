// src/EditorPage.js
import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Editor } from '@monaco-editor/react';
import io from 'socket.io-client';
import sendRequest from '../util/sendRequest';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

const EditorPage = () => {
  const { pageId } = useParams(); // Retrieve pageId from the URL
  const [code, setCode] = useState("// Loading...");
  const editorRef = useRef(null);
  const isRemoteUpdate = useRef(false);
  const socketRef = useRef(null);

  // Initialize socket connection
  useEffect(() => {
    const socket = io(BACKEND_URL, {
      transports: ['websocket']
    });
    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, []);

  // Fetch the page content when the component loads
  useEffect(() => {
    const socket = socketRef.current;
    if (!socket) return;

    const fetchPage = async () => {
        const response = await sendRequest(`/pages/${pageId}`);
        if (!response.ok) throw new Error('Page not found');

        const data = await response.json();
        setCode(data.content);
    };

    fetchPage();

    // Listen for real-time updates
    const handleUpdate = (data) => {
      if (data.id === pageId) {
        isRemoteUpdate.current = true;
        setCode(data.content);
      }
    };

    socket.on('code_update', handleUpdate);

    return () => socket.off('code_update', handleUpdate); // Cleanup listener on unmount
  }, [pageId]);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;

    editor.onDidChangeModelContent(() => {
      if (isRemoteUpdate.current) {
        isRemoteUpdate.current = false;
        return;
      }
      const newContent = editorRef.current.getValue();
      socketRef.current.emit('code_edit', { id: pageId, content: newContent });
    });
  };

  return (
    <div style={{ height: "100vh" }}>
      <Editor
        height="100%"
        language="javascript"
        value={code}
        onMount={handleEditorDidMount}
        theme="vs-dark"
      />
    </div>
  );
};

export default EditorPage;
