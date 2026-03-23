import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { fetchGuides, fetchGuideContent } from "../hooks/useQuery";

export default function GuidesPage() {
  const [guides, setGuides] = useState({});
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGuides()
      .then(setGuides)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleDomainClick = async (domain) => {
    setSelectedDomain(domain);
    setContent(null);
    try {
      const data = await fetchGuideContent(domain);
      setContent(data.content);
    } catch (err) {
      setContent(`Error loading guide: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="response-area loading">
        <div className="spinner" />
      </div>
    );
  }

  if (selectedDomain && content !== null) {
    return (
      <div>
        <button
          className="domain-chip"
          onClick={() => { setSelectedDomain(null); setContent(null); }}
          style={{ marginBottom: "var(--space-4)" }}
          type="button"
        >
          &larr; Back to guides
        </button>
        <div className="response-area">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 style={{
        fontFamily: "var(--font-mono)",
        fontSize: "1.125rem",
        color: "var(--color-accent)",
        marginBottom: "var(--space-6)",
      }}>
        Knowledge Guides
      </h1>

      <div className="guide-grid">
        {Object.entries(guides)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([domain, info]) => (
            <button
              key={domain}
              className="guide-card"
              onClick={() => info.available && handleDomainClick(domain)}
              disabled={!info.available}
              style={{ textAlign: "left", border: info.available ? undefined : "1px solid var(--color-border)" }}
              type="button"
            >
              <div className="guide-card-title">
                {domain.replace(/_/g, " ")}
                {!info.available && (
                  <span style={{ color: "var(--color-text-muted)", fontWeight: 400 }}> (unavailable)</span>
                )}
              </div>
              <div className="guide-card-topics">{info.topics}</div>
            </button>
          ))}
      </div>
    </div>
  );
}
