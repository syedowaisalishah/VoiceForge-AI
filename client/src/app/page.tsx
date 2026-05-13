"use client";

import { useState, useEffect } from "react";

interface Persona {
  id: string;
  name: string;
  description: string;
}

interface PostType {
  id: string;
  label: string;
  description: string;
}

const MOODS = [
  { id: "proud",       label: "Proud 💪"      },
  { id: "reflective",  label: "Reflective 🤔"  },
  { id: "frustrated",  label: "Frustrated 😡"  },
  { id: "grateful",    label: "Grateful 🙏"    },
  { id: "determined",  label: "Determined 🔥"  },
  { id: "hyped",       label: "Hyped 🚀"       },
  { id: "grinding",    label: "Grinding ⚙️"    },
  { id: "exhausted",   label: "Exhausted 😮‍💨"  },
];

export default function Home() {
  const [personas, setPersonas]             = useState<Persona[]>([]);
  const [postTypes, setPostTypes]           = useState<PostType[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<string>("zack");
  const [platform, setPlatform]             = useState<string>("X");
  const [selectedPostType, setSelectedPostType] = useState<string>("");
  const [selectedMood, setSelectedMood]     = useState<string>("");
  const [brief, setBrief]                   = useState<string>("");
  const [result, setResult]                 = useState<string>("");
  const [loading, setLoading]               = useState<boolean>(false);
  const [error, setError]                   = useState<string>("");
  const [copied, setCopied]                 = useState<boolean>(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  useEffect(() => {
    fetchPersonas();
  }, []);

  // Whenever the persona changes, load its post types
  useEffect(() => {
    if (selectedPersona) {
      fetchPostTypes(selectedPersona);
      setSelectedPostType(""); // reset post type on persona switch
    }
  }, [selectedPersona]);

  const fetchPersonas = async () => {
    try {
      const response = await fetch(`${backendUrl}/personas`);
      const data = await response.json();
      setPersonas(data);
    } catch (err) {
      console.error("Failed to fetch personas:", err);
      setPersonas([
        { id: "zack", name: "Zack", description: "Street-level entrepreneur. Raw, reactive, no filter." },
        { id: "alex", name: "Alex", description: "The thoughtful builder. Narrative-driven, emotionally honest." },
      ]);
    }
  };

  const fetchPostTypes = async (personaId: string) => {
    try {
      const response = await fetch(`${backendUrl}/post-types/${personaId}`);
      if (response.ok) {
        const data = await response.json();
        setPostTypes(data);
      }
    } catch (err) {
      console.error("Failed to fetch post types:", err);
    }
  };

  const handleGenerate = async () => {
    if (!brief.trim()) return;
    setLoading(true);
    setError("");
    setResult("");
    setCopied(false);

    try {
      const response = await fetch(`${backendUrl}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          persona:   selectedPersona,
          platform:  platform,
          brief:     brief,
          post_type: selectedPostType || undefined,
          mood:      selectedMood || undefined,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setResult(data.content);
      } else {
        setError(data.detail || "Something went wrong");
      }
    } catch (err) {
      setError(`Failed to connect to backend at ${backendUrl}. Is the server running?`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const selectedPostTypeObj = postTypes.find(pt => pt.id === selectedPostType);

  return (
    <main className="main-container">
      <div className="page-header">
        <h1>VoiceForge AI</h1>
        <p className="subtitle">Authentic social media posts in any writer's voice — no AI filler, no hallucinated facts.</p>
      </div>

      <div className="dashboard-grid">
        {/* ── Left Column: Controls ─────────────────────────────────── */}
        <div className="card controls-card">

          {/* 1. Select Writer */}
          <section className="control-section">
            <h2 className="section-title"><span className="step-num">1</span>Select Writer</h2>
            <div className="persona-selector">
              {personas.map((p) => (
                <div
                  key={p.id}
                  id={`persona-${p.id}`}
                  className={`persona-option ${selectedPersona === p.id ? "active" : ""}`}
                  onClick={() => setSelectedPersona(p.id)}
                >
                  <div className="persona-avatar">{p.name[0]}</div>
                  <div className="persona-text">
                    <div className="persona-name">{p.name}</div>
                    <div className="persona-desc">{p.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 2. Platform */}
          <section className="control-section">
            <h2 className="section-title"><span className="step-num">2</span>Target Platform</h2>
            <div className="platform-selector">
              {["X", "Facebook"].map((pl) => (
                <button
                  key={pl}
                  id={`platform-${pl.toLowerCase()}`}
                  className={`platform-btn ${platform === pl ? "active" : ""}`}
                  onClick={() => setPlatform(pl)}
                >
                  {pl === "X" ? "𝕏 Twitter" : "📘 Facebook"}
                </button>
              ))}
            </div>
          </section>

          {/* 3. Post Type */}
          <section className="control-section">
            <h2 className="section-title"><span className="step-num">3</span>Post Type <span className="optional-tag">optional but recommended</span></h2>
            <select
              id="post-type-select"
              className="post-type-select"
              value={selectedPostType}
              onChange={(e) => setSelectedPostType(e.target.value)}
            >
              <option value="">— Let the AI decide —</option>
              {postTypes.map((pt) => (
                <option key={pt.id} value={pt.id}>{pt.label}</option>
              ))}
            </select>
            {selectedPostTypeObj && (
              <p className="post-type-description">{selectedPostTypeObj.description}</p>
            )}
          </section>

          {/* 4. Mood */}
          <section className="control-section">
            <h2 className="section-title"><span className="step-num">4</span>Mood <span className="optional-tag">optional</span></h2>
            <div className="mood-selector">
              {MOODS.map((m) => (
                <button
                  key={m.id}
                  id={`mood-${m.id}`}
                  className={`mood-btn ${selectedMood === m.id ? "active" : ""}`}
                  onClick={() => setSelectedMood(selectedMood === m.id ? "" : m.id)}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </section>

          {/* 5. The Brief */}
          <section className="control-section">
            <h2 className="section-title"><span className="step-num">5</span>The Brief</h2>
            <div className="brief-guidance">
              <strong>Facts only.</strong> Give raw numbers, job details, outcomes — don't write the post yourself. The AI will invent nothing beyond what you give it.
            </div>
            <textarea
              id="brief-input"
              className="brief-textarea"
              placeholder={"Examples:\n• Post-construction clean, 5,200 sqft, charged $2,340, labor $945, profit $1,395. Got her locked in for bi-weekly.\n• Worst week: lost 3 cleaners, $14K unassigned on the schedule. Need help finding new ones fast.\n• July recap: revenue $17,572.49, labor $8,471.25, ad spend $1,888.45, profit $6,507.12."}
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
            />
            <div className="char-count">{brief.length} chars</div>
          </section>

          <button
            id="generate-btn"
            className="generate-btn"
            onClick={handleGenerate}
            disabled={loading || !brief.trim()}
          >
            {loading ? (
              <>
                <span className="loader"></span>
                Generating…
              </>
            ) : (
              "✦ Generate Post"
            )}
          </button>

          {error && (
            <div className="error-msg">{error}</div>
          )}
        </div>

        {/* ── Right Column: Output ──────────────────────────────────── */}
        <div className="card result-card">
          <div className="result-header">
            <h2 className="section-title">Output Preview</h2>
            {result && (
              <div className="result-meta">
                <span className="result-badge">{selectedPersona.charAt(0).toUpperCase() + selectedPersona.slice(1)}</span>
                {selectedPostType && <span className="result-badge">{selectedPostType.replace(/_/g, " ")}</span>}
                <span className="result-badge">{platform}</span>
              </div>
            )}
          </div>

          <div className={`result-content ${result ? "has-content" : ""}`}>
            {result ? (
              <pre className="result-pre">{result}</pre>
            ) : (
              <div className="placeholder-text">
                <div className="placeholder-icon">✦</div>
                <div>Your generated post will appear here.</div>
                <div className="placeholder-hint">Fill in the brief and hit Generate Post.</div>
              </div>
            )}
          </div>

          {result && (
            <div className="result-actions">
              <button
                id="copy-btn"
                className={`copy-btn ${copied ? "copied" : ""}`}
                onClick={handleCopy}
              >
                {copied ? "✓ Copied!" : "Copy to Clipboard"}
              </button>
              <button
                id="regenerate-btn"
                className="regenerate-btn"
                onClick={handleGenerate}
                disabled={loading}
              >
                ↺ Regenerate
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
