// src/Dashboard.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import sendRequest from "../util/sendRequest";
import '../style/dashboard.css';

const Dashboard = () => {
  const [pageId, setPageId] = useState("");
  const navigate = useNavigate();

  const handleCreatePage = async () => {
    try {
      const response = await sendRequest("new-page");
    
      if (response.redirected) {
        let newUrl = response.url.split("/");
        newUrl = "/" + newUrl[newUrl.length - 2] + "/" + newUrl[newUrl.length - 1];
        navigate(newUrl);
      } else {
        console.error("Failed to create new page.");
      }
    } catch (error) {
      console.error("Error creating new page:", error);
    }
  };

  const handleOpenPage = () => {
    if (pageId) {
      navigate(`/pages/${pageId}`);
    } else {
      alert("Please enter a valid Page ID.");
    }
  };

  return (
    <div
      className="dashboard"
      style={{ textAlign: "center", marginTop: "50px" }}
    >
      <h1>Collaborative Code Editor</h1>

      <button onClick={handleCreatePage} style={{ margin: "10px" }}>
        Create New Page
      </button>

      <div style={{ marginTop: "20px" }}>
        <input
          type="text"
          value={pageId}
          onChange={(e) => setPageId(e.target.value)}
          placeholder="Enter Page ID"
          style={{ padding: "5px", width: "200px" }}
        />
        <button onClick={handleOpenPage} style={{ marginLeft: "10px" }}>
          Open Page
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
