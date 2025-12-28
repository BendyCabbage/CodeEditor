import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import EditorPage from './components/EditorPage';
import Dashboard from './components/Dashboard';
import ProjectDashboard from './components/ProjectDashboard';
import ProjectEditor from './components/ProjectEditor';
import NotFound from './components/NotFound';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<ProjectDashboard />} />
        <Route path="/legacy-dashboard" element={<Dashboard />} />
        <Route path="/pages/:pageId" element={<EditorPage />} />
        <Route path="/projects/:projectId" element={<ProjectEditor />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export default App;