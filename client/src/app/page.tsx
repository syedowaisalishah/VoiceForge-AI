"use client";

import { useState, useEffect } from "react";

interface Persona {
  id: string;
  name: string;
  description: string;
}

interface ToneOption {
  id: string;
  label: string;
  emoji: string;
  description: string;
}

interface AudienceOption {
  id: string;
  label: string;
  emoji: string;
}

interface XFormatOption {
  id: string;
  label: string;
  emoji: string;
  description: string;
  preview: string;
}

export default function Home() {
  const [personas, setPersonas]               = useState<Persona[]>([]);
  const [tones, setTones]                     = useState<ToneOption[]>([]);
  const [audiences, setAudiences]             = useState<AudienceOption[]>([]);
  const [xFormats, setXFormats]               = useState<XFormatOption[]>([]);

  const [selectedPersona, setSelectedPersona] = useState<string>("zack");
  const [platform, setPlatform]               = useState<string>("X");
  const [selectedTone, setSelectedTone]       = useState<string>("");
  const [selectedAudience, setSelectedAudience] = useState<string>("");
  const [customAudience, setCustomAudience]   = useState<string>("");
  const [selectedXFormat, setSelectedXFormat] = useState<string>("ai_decide");
  const [brief, setBrief]                     = useState<string>("");
  const [result, setResult]                   = useState<string>("");
  const [loading, setLoading]                 = useState<boolean>(false);
  const [error, setError]                     = useState<string>("");
  const [copied, setCopied]                   = useState<boolean>(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  useEffect(() => {
    fetchPersonas();
    fetchTones();
    fetchAudiences();
    fetchXFormats();
  }, []);

  // When platform changes away from X, reset x_format
  useEffect(() => {
    if (platform !== "X") setSelectedXFormat("ai_decide");
  }, [platform]);

  const fetchPersonas = async () => {
    try {
      const res  = await fetch(`${backendUrl}/personas`);
      const data = await res.json();
      setPersonas(data);
    } catch {
      setPersonas([
        { id: "zack", name: "Zack", description: "Street-level entrepreneur. Raw, reactive, no filter." },
        { id: "alex", name: "Alex", description: "The thoughtful builder. Narrative-driven, emotionally honest." },
        { id: "pj", name: "PJ", description: "Remote SMB founder. Lifestyle freedom, strict rules, exit-focused." },
      ]);
    }
  };

  const fetchTones = async () => {
    try {
      const res = await fetch(`${backendUrl}/tones`);
      if (res.ok) setTones(await res.json());
    } catch {
      setTones([
        { id: "raw",          label: "Raw & Unfiltered",    emoji: "🔥", description: "No polish. Like a voice note." },
        { id: "story",        label: "Story",               emoji: "📖", description: "Narrative arc: setup, turn, close." },
        { id: "controversial",label: "Controversial Take",  emoji: "⚡", description: "Bold claim people will argue with." },
        { id: "humble_brag",  label: "Humble Brag",         emoji: "😏", description: "Achievement, but grounded." },
        { id: "rant",         label: "Rant",                emoji: "😤", description: "Controlled frustration with clarity." },
        { id: "lesson",       label: "Lesson Learned",      emoji: "💡", description: "What happened and what it taught." },
        { id: "hype",         label: "Hype",                emoji: "🚀", description: "Big energy. Announcement-style." },
        { id: "question",     label: "Question / Open Loop", emoji: "🤔", description: "Opens a conversation, ends with a hook." },
      ]);
    }
  };

  const fetchAudiences = async () => {
    try {
      const res = await fetch(`${backendUrl}/audiences`);
      if (res.ok) setAudiences(await res.json());
    } catch {
      setAudiences([
        { id: "founders",      label: "Entrepreneurs / Founders",    emoji: "💼" },
        { id: "beginners",     label: "Beginners / New People",       emoji: "🌱" },
        { id: "service_biz",   label: "Service Business Owners",      emoji: "🔧" },
        { id: "personal_brand",label: "Personal Brand Builders",      emoji: "📱" },
        { id: "general",       label: "General Public",               emoji: "🌍" },
        { id: "custom",        label: "Custom (specify below)",       emoji: "✏️" },
      ]);
    }
  };

  const fetchXFormats = async () => {
    try {
      const res = await fetch(`${backendUrl}/x-formats`);
      if (res.ok) setXFormats(await res.json());
    } catch {
      setXFormats([
        { id: "two_liner",  label: "2-Liner",       emoji: "⚡", description: "Punchy. Under 140 chars.",              preview: "──────────────────────────\n─────────────────" },
        { id: "four_liner", label: "4-Liner",        emoji: "📝", description: "3–4 short lines. One idea per line.",  preview: "──────────────────────────────\n────────────────────\n──────────────────────────\n─────────────" },
        { id: "mid_length", label: "Mid-Length",     emoji: "📄", description: "5–8 lines. Paragraph + kicker.",       preview: "───────────────────────────────────\n\n────── ─────────── ──────\n─────────────────────────────\n\n─────────────────────" },
        { id: "thread",     label: "Thread",         emoji: "🧵", description: "Numbered tweets. Hook → Points → Close.", preview: "1/ ──────────────────────────────────\n\n2/ ─────── ──────────────────\n\n3/ ──────────── ─────────────\n\n4/ ─────────────────────────── ↩" },
        { id: "ai_decide",  label: "Auto (Best Fit)",  emoji: "🎯", description: "System picks the right length.",            preview: "" },
      ]);
    }
  };

  const handleGenerate = async () => {
    if (!brief.trim()) return;
    setLoading(true);
    setError("");
    setResult("");
    setCopied(false);
    try {
      const body: Record<string, string | undefined> = {
        persona:         selectedPersona,
        platform,
        brief,
        tone:            selectedTone        || undefined,
        target_audience: selectedAudience    || undefined,
        custom_audience: (selectedAudience === "custom" && customAudience.trim()) ? customAudience.trim() : undefined,
        x_format:        (platform === "X" && selectedXFormat) ? selectedXFormat : undefined,
      };

      const res = await fetch(`${backendUrl}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
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

  const selectedToneObj     = tones.find(t => t.id === selectedTone);
  const selectedAudienceObj = audiences.find(a => a.id === selectedAudience);
  const selectedXFormatObj  = xFormats.find(f => f.id === selectedXFormat);

  let stepNum = 1;

  return (
    <div className="app-wrapper">
      <div className="glow-blob blob-1"></div>
      <div className="glow-blob blob-2"></div>
      <div className="glow-blob blob-3"></div>

      <main className="main-container">

        {/* Header */}
        <div className="page-header">
          <div className="header-tag">✨ AI-Powered Voice Replication</div>
          <h1>VoiceForge AI</h1>
          <p className="subtitle">Authentic posts in any writer&apos;s voice. No AI filler, no hallucinated facts.</p>
        </div>

        {/* ── Step 1: Writer ─────────────────────────────── */}
        <div className="card">
          <h2 className="section-title"><span className="step-num">{stepNum++}</span>Select Writer</h2>
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
          <h2 className="section-title"><span className="step-num">{stepNum++}</span>Target Platform</h2>
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

        {/* ── Step 3: X Post Format (only when X selected) ── */}
        {platform === "X" && (
          <div className="card">
            <h2 className="section-title">
              <span className="step-num">{stepNum++}</span>Post Format
              <span className="optional-tag">shapes the output length</span>
            </h2>
            <div className="x-format-grid">
              {xFormats.map((fmt) => (
                <div
                  key={fmt.id}
                  id={`format-${fmt.id}`}
                  className={`x-format-card ${selectedXFormat === fmt.id ? "active" : ""}`}
                  onClick={() => setSelectedXFormat(fmt.id)}
                >
                  <div className="x-format-card-header">
                    <span className="x-format-emoji">{fmt.emoji}</span>
                    <span className="x-format-label">{fmt.label}</span>
                  </div>
                  <div className="x-format-desc">{fmt.description}</div>
                  {fmt.preview && (
                    <div className="x-format-preview">{fmt.preview}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Step 4: Writing Tone ─────────────────────────── */}
        <div className="card">
          <h2 className="section-title">
            <span className="step-num">{stepNum++}</span>Writing Tone
            <span className="optional-tag">the angle of this post</span>
          </h2>
          <div className="tone-grid">
            {tones.map((t) => (
              <div
                key={t.id}
                id={`tone-${t.id}`}
                className={`tone-pill ${selectedTone === t.id ? "active" : ""}`}
                onClick={() => setSelectedTone(selectedTone === t.id ? "" : t.id)}
              >
                <span className="tone-pill-emoji">{t.emoji}</span>
                <div className="tone-pill-body">
                  <span className="tone-pill-label">{t.label}</span>
                  <span className="tone-pill-desc">{t.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Step 5: Target Audience ──────────────────────── */}
        <div className="card">
          <h2 className="section-title">
            <span className="step-num">{stepNum++}</span>Target Audience
            <span className="optional-tag">shapes vocabulary &amp; depth</span>
          </h2>
          <div className="audience-grid">
            {audiences.map((a) => (
              <button
                key={a.id}
                id={`audience-${a.id}`}
                className={`audience-btn ${selectedAudience === a.id ? "active" : ""}`}
                onClick={() => setSelectedAudience(selectedAudience === a.id ? "" : a.id)}
              >
                <span className="audience-emoji">{a.emoji}</span>
                <span className="audience-label">{a.label}</span>
              </button>
            ))}
          </div>
          {selectedAudience === "custom" && (
            <input
              id="custom-audience-input"
              type="text"
              className="custom-audience-input"
              placeholder='e.g. "HVAC business owners in Texas" or "indie game developers"'
              value={customAudience}
              onChange={(e) => setCustomAudience(e.target.value)}
            />
          )}
        </div>

        {/* ── Step 6: Brief + Generate ─────────────────────── */}
        <div className="card">
          <h2 className="section-title"><span className="step-num">{stepNum++}</span>The Brief</h2>
          <div className="brief-guidance">
            <strong>Facts only.</strong> Give raw numbers, job details, outcomes. Don&apos;t write the post yourself.
          </div>
          <textarea
            id="brief-input"
            className="brief-textarea"
            placeholder={"Examples:\n• Revenue $17,572 · Labor $8,471 · Profit $6,507 | July recap\n• Lost 3 cleaners this week, $14K unassigned on the schedule\n• Post-construction clean, 5,200 sqft, charged $2,340, profit $1,395"}
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
                  <span className="result-badge badge-persona">{selectedPersona}</span>
                  <span className="result-badge badge-platform">{platform}</span>
                  {selectedXFormat && selectedXFormat !== "ai_decide" && selectedXFormatObj && (
                    <span className="result-badge format-badge">{selectedXFormatObj.emoji} {selectedXFormatObj.label}</span>
                  )}
                  {selectedTone && selectedToneObj && (
                    <span className="result-badge tone-badge">{selectedToneObj.emoji} {selectedToneObj.label}</span>
                  )}
                  {selectedAudience && selectedAudienceObj && (
                    <span className="result-badge audience-badge">
                      {selectedAudienceObj.emoji} {selectedAudience === "custom" && customAudience ? customAudience : selectedAudienceObj.label}
                    </span>
                  )}
                </div>
              )}
            </div>

            <div className="output-window">
              <div className="output-window-header">
                <div className="window-dots">
                  <div className="window-dot red"></div>
                  <div className="window-dot yellow"></div>
                  <div className="window-dot green"></div>
                </div>
                <div className="window-title">{selectedPersona} // {platform}</div>
              </div>
              <div className={`result-content ${result ? "has-content" : ""}`}>
                {result
                  ? <pre className="result-pre">{result}</pre>
                  : <div className="placeholder-text">
                      <span className="loader" style={{ marginBottom: '0.5rem' }} />
                      Generating your post…
                    </div>
                }
              </div>
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
    </div>
  );
}
