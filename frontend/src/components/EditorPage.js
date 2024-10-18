// src/EditorPage.js
import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Editor } from '@monaco-editor/react';
import io from 'socket.io-client';
import sendRequest from '../util/sendRequest';

const socket = io('http://localhost:5000'); // Connect to the backend

const EditorPage = () => {
  const { pageId } = useParams(); // Retrieve pageId from the URL
  const [code, setCode] = useState("// Loading...");
  const editorRef = useRef(null);

  // Fetch the page content when the component loads
  useEffect(() => {
    const fetchPage = async () => {
        const response = await sendRequest(`/pages/${pageId}`);
        if (!response.ok) throw new Error('Page not found');

        const data = await response.json();
        setCode(data.content);
    };

    fetchPage();

    // Listen for real-time updates
    socket.on('code_update', (data) => {
      if (data.id === pageId) {
        setCode(data.content);
      }
    });

    return () => socket.off('code_update'); // Cleanup listener on unmount
  }, [pageId]);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;

    editor.onDidChangeModelContent(() => {
      const newContent = editorRef.current.getValue();
      socket.emit('code_edit', { id: pageId, content: newContent });
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
