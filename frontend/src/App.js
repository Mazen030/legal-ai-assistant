import React, { useState } from 'react';
import UploadZone from './components/UploadZone';
import ChatInterface from './components/ChatInterface';
import { uploadDocument } from './services/api';
import './App.css';

function App() {
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await uploadDocument(file);
      setSession(result);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSession = () => {
    setSession(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">⚖️</span>
          <span className="logo-text">LegalAI</span>
          <span className="logo-tag">Document Assistant</span>
        </div>
      </header>

      <main className="app-main">
        {!session ? (
          <div className="landing">
            <h1 className="landing-title">
              Understand any legal document,<br />
              <span className="accent">instantly.</span>
            </h1>
            <p className="landing-sub">
              Upload a contract, agreement, or policy document and ask questions in plain English.
            </p>
            <UploadZone onUpload={handleUpload} isLoading={isLoading} />
            {error && <div className="error-banner">⚠️ {error}</div>}
          </div>
        ) : (
          <ChatInterface session={session} onNewSession={handleNewSession} />
        )}
      </main>
    </div>
  );
}

export default App;
