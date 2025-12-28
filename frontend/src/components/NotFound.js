import React from 'react';
import '../style/project-editor.css';

const NotFound = () => {
  return (
    <div className="project-editor error-state">
      <div className="error-content">
        <h2>404</h2>
        <p>Page not found</p>
      </div>
    </div>
  );
};

export default NotFound;

