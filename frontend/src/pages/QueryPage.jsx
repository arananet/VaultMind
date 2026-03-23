import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { useVaultQuery, synthesizeSpeech } from "../hooks/useQuery";

const DOMAINS = [
  "Medicine", "Chemistry", "Energy", "Agriculture", "Water",
  "Construction", "Communications", "Metalworking", "Navigation",
  "Security", "Radio International",
];

export default function QueryPage() {
  const [input, setInput] = useState("");
  const { query, loading, error, result } = useVaultQuery();
  const textareaRef = useRef(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (input.trim() && !loading) {
      query(input.trim());
    }
  };

  const handleDomainClick = (domain) => {
    setInput(`What are the key procedures for ${domain.toLowerCase()}?`);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTTS = async () => {
    if (!result?.answer) return;
    try {
      const blob = await synthesizeSpeech(result.answer);
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
      audio.onended = () => URL.revokeObjectURL(url);
    } catch {
      /* TTS not available — silent fail */
    }
  };

  return (
    <div>
      <section className="domain-chips" role="group" aria-label="Knowledge domains">
        {DOMAINS.map((d) => (
          <button
            key={d}
            className="domain-chip"
            onClick={() => handleDomainClick(d)}
            type="button"
          >
            {d}
          </button>
        ))}
      </section>

      <form onSubmit={handleSubmit}>
        <div className="query-input-wrapper">
          <textarea
            ref={textareaRef}
            className="query-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter your survival query... (Enter to submit, Shift+Enter for newline)"
            aria-label="Query input"
            rows={3}
          />
          <button
            className="query-submit"
            type="submit"
            disabled={loading || !input.trim()}
          >
            {loading ? "..." : "QUERY"}
          </button>
        </div>
      </form>

      {error && (
        <div className="card" style={{ borderColor: "var(--color-fail)", marginBottom: "var(--space-4)" }}>
          <div className="card-header" style={{ color: "var(--color-fail)" }}>Error</div>
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="response-area loading">
          <div className="spinner" role="status" aria-label="Loading" />
        </div>
      )}

      {result && !loading && (
        <div className="response-area">
          <ReactMarkdown>{result.answer}</ReactMarkdown>

          <div className="response-meta">
            <span className="badge">Service: {result.service}</span>
            {result.sources?.map((s, i) => (
              <span key={i} className="badge">{s}</span>
            ))}
            <button className="tts-button" onClick={handleTTS} type="button" aria-label="Read aloud">
              Read Aloud
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
