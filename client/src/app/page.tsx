"use client";

import { useState, useEffect } from "react";

interface Persona {
  id: string;
  name: string;
  description: string;
}

export default function Home() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<string>("zack");
  const [platform, setPlatform] = useState<string>("X");
  const [brief, setBrief] = useState<string>("");
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    fetchPersonas();
  }, []);

  const fetchPersonas = async () => {
    try {
      const response = await fetch("http://localhost:8000/personas");
      const data = await response.json();
      setPersonas(data);
    } catch (err) {
      console.error("Failed to fetch personas", err);
      // Fallback for demo if backend is not yet running
      setPersonas([
        { id: "zack", name: "Zack", description: "Bold and direct, business-focused." },
        { id: "alex", name: "Alex", description: "Confident, storytelling entrepreneur." }
      ]);
    }
  };

  const handleGenerate = async () => {
    if (!brief) return;
    setLoading(true);
    setError("");
    setResult("");

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          persona: selectedPersona,
          platform: platform,
          brief: brief,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setResult(data.content);
      } else {
        setError(data.detail || "Something went wrong");
      }
    } catch (err) {
      setError("Failed to connect to backend. Make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="main-container">
      <h1>VoiceForge AI</h1>
      <p className="subtitle">Authentic social media posts in any writer's voice.</p>

      <div className="dashboard-grid">
        {/* Left Column: Controls */}
        <div className="card">
          <div className="persona-section">
            <h2 className="section-title">1. Select Style</h2>
            <div className="persona-selector">
              {personas.map((p) => (
                <div
                  key={p.id}
                  className={`persona-option ${selectedPersona === p.id ? "active" : ""}`}
                  onClick={() => setSelectedPersona(p.id)}
                >
                  <div className="persona-name">{p.name}</div>
                  <div className="persona-desc">{p.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="platform-section">
            <h2 className="section-title">2. Target Platform</h2>
            <div className="platform-selector">
              <button
                className={`platform-btn ${platform === "X" ? "active" : ""}`}
                onClick={() => setPlatform("X")}
              >
                𝕏 (Twitter)
              </button>
              <button
                className={`platform-btn ${platform === "Facebook" ? "active" : ""}`}
                onClick={() => setPlatform("Facebook")}
              >
                Facebook
              </button>
            </div>
          </div>

          <div className="input-area">
            <h2 className="section-title">3. The Brief (Context)</h2>
            <textarea
              placeholder="What should the post be about? Give me 2-3 lines of facts..."
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
            />
          </div>

          <button
            className="generate-btn"
            onClick={handleGenerate}
            disabled={loading || !brief}
          >
            {loading ? (
              <>
                <span className="loader"></span>
                Generating...
              </>
            ) : (
              "Generate Post"
            )}
          </button>
          {error && <p style={{ color: "#ff4d4d", marginTop: "1rem", fontSize: "0.9rem" }}>{error}</p>}
        </div>

        {/* Right Column: Output */}
        <div className="card result-card">
          <h2 className="section-title">Output Preview</h2>
          <div className="result-content">
            {result ? (
              result
            ) : (
              <div className="placeholder-text">
                Your generated post will appear here...
              </div>
            )}
          </div>
          {result && (
            <button
              className="platform-btn"
              style={{ marginTop: "1rem", width: "100%", background: "var(--glass)" }}
              onClick={() => navigator.clipboard.writeText(result)}
            >
              Copy to Clipboard
            </button>
          )}
        </div>
      </div>
    </main>
  );
}
