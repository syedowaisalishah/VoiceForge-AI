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
  { id: "proud",       label: "Proud 💪"     },
  { id: "reflective",  label: "Reflective 🤔" },
  { id: "frustrated",  label: "Frustrated 😡" },
  { id: "grateful",    label: "Grateful 🙏"   },
  { id: "determined",  label: "Determined 🔥" },
  { id: "hyped",       label: "Hyped 🚀"      },
  { id: "grinding",    label: "Grinding ⚙️"   },
  { id: "exhausted",   label: "Exhausted 😮‍💨" },
];

export default function Home() {
  const [personas, setPersonas]               = useState<Persona[]>([]);
  const [postTypes, setPostTypes]             = useState<PostType[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<string>("zack");
  const [platform, setPlatform]               = useState<string>("X");
  const [selectedPostType, setSelectedPostType] = useState<string>("");
  const [selectedMood, setSelectedMood]       = useState<string>("");
  const [brief, setBrief]                     = useState<string>("");
  const [result, setResult]                   = useState<string>("");
  const [loading, setLoading]                 = useState<boolean>(false);
  const [error, setError]                     = useState<string>("");
  const [copied, setCopied]                   = useState<boolean>(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  useEffect(() => { fetchPersonas(); }, []);

  useEffect(() => {
    if (selectedPersona) {
      fetchPostTypes(selectedPersona);
      setSelectedPostType("");
    }
  }, [selectedPersona]);

  const fetchPersonas = async () => {
    try {
      const res  = await fetch(`${backendUrl}/personas`);
      const data = await res.json();
      setPersonas(data);
    } catch {
      setPersonas([
        { id: "zack", name: "Zack", description: "Street-level entrepreneur. Raw, reactive, no filter." },
        { id: "alex", name: "Alex", description: "The thoughtful builder. Narrative-driven, emotionally honest." },
      ]);
    }
  };

  const fetchPostTypes = async (personaId: string) => {
    try {
      const res = await fetch(`${backendUrl}/post-types/${personaId}`);
      if (res.ok) setPostTypes(await res.json());
    } catch { /* silent */ }
  };

  const handleGenerate = async () => {
    if (!brief.trim()) return;
    setLoading(true);
    setError("");
    setResult("");
    setCopied(false);
    try {
      const res = await fetch(`${backendUrl}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          persona:   selectedPersona,
          platform,
          brief,
          post_type: selectedPostType || undefined,
          mood:      selectedMood     || undefined,
        }),
      });
      const data = await res.json();
      if (res.ok) setResult(data.content);
      else        setError(data.detail || "Something went wrong.");
    } catch {
      setError(`Cannot reach backend at ${backendUrl}. Is the server running?`);
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

      {/* Header */}
      <div className="page-header">
        <h1>VoiceForge AI</h1>
        <p className="subtitle">Authentic posts in any writer's voice — no AI filler, no hallucinated facts.</p>
      </div>

      {/* ── Step 1: Writer ─────────────────────────────── */}
      <div className="card">
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
              <div style={{ minWidth: 0 }}>
                <div className="persona-name">{p.name}</div>
                <div className="persona-desc">{p.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Step 2: Platform ───────────────────────────── */}
      <div className="card">
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
      </div>

      {/* ── Step 3: Post Type ──────────────────────────── */}
      <div className="card">
        <h2 className="section-title">
          <span className="step-num">3</span>Post Type
          <span className="optional-tag">optional but recommended</span>
        </h2>
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
          <p className="post-type-desc">{selectedPostTypeObj.description}</p>
        )}
      </div>

      {/* ── Step 4: Mood ───────────────────────────────── */}
      <div className="card">
        <h2 className="section-title">
          <span className="step-num">4</span>Mood
          <span className="optional-tag">optional</span>
        </h2>
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
      </div>

      {/* ── Step 5: Brief + Generate ───────────────────── */}
      <div className="card">
        <h2 className="section-title"><span className="step-num">5</span>The Brief</h2>
        <div className="brief-guidance">
          <strong>Facts only.</strong> Give raw numbers, job details, outcomes — don&apos;t write the post yourself.
        </div>
        <textarea
          id="brief-input"
          className="brief-textarea"
          placeholder={"Examples:\n• Revenue $17,572 · Labor $8,471 · Profit $6,507 — July recap\n• Lost 3 cleaners this week, $14K unassigned on the schedule\n• Post-construction clean, 5,200 sqft, charged $2,340, profit $1,395"}
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
        />
        <div className="char-count">{brief.length} chars</div>

        <button
          id="generate-btn"
          className="generate-btn"
          style={{ marginTop: "1rem" }}
          onClick={handleGenerate}
          disabled={loading || !brief.trim()}
        >
          {loading
            ? <><span className="loader" /> Generating…</>
            : "✦ Generate Post"
          }
        </button>

        {error && <div className="error-msg">{error}</div>}
      </div>

      {/* ── Output ─────────────────────────────────────── */}
      {(result || loading) && (
        <div className="card">
          <div className="result-header">
            <h2 className="section-title" style={{ marginBottom: 0 }}>Output Preview</h2>
            {result && (
              <div className="result-meta">
                <span className="result-badge">{selectedPersona}</span>
                {selectedPostType && <span className="result-badge">{selectedPostType.replace(/_/g, " ")}</span>}
                <span className="result-badge">{platform}</span>
              </div>
            )}
          </div>

          <div className={`result-content ${result ? "has-content" : ""}`}>
            {result
              ? <pre className="result-pre">{result}</pre>
              : <div className="placeholder-text">Generating your post…</div>
            }
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
      )}

    </main>
  );
}
