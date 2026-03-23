import { useState, useEffect, useCallback } from "react";
import { fetchDiagnostics } from "../hooks/useQuery";

const STATUS_LABELS = {
  ok: { text: "OK", className: "status-ok" },
  warn: { text: "WARN", className: "status-warn" },
  fail: { text: "FAIL", className: "status-fail" },
};

export default function DiagnosticsPage() {
  const [diagnostics, setDiagnostics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDiagnostics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDiagnostics();
      setDiagnostics(data.diagnostics || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDiagnostics();
  }, [loadDiagnostics]);

  const counts = diagnostics.reduce(
    (acc, d) => {
      acc[d.status] = (acc[d.status] || 0) + 1;
      return acc;
    },
    {}
  );

  return (
    <div>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "var(--space-6)",
      }}>
        <h1 style={{
          fontFamily: "var(--font-mono)",
          fontSize: "1.125rem",
          color: "var(--color-accent)",
        }}>
          System Diagnostics
        </h1>
        <button
          className="domain-chip"
          onClick={loadDiagnostics}
          disabled={loading}
          type="button"
        >
          {loading ? "Running..." : "Re-run"}
        </button>
      </div>

      {error && (
        <div className="card" style={{ borderColor: "var(--color-fail)", marginBottom: "var(--space-4)" }}>
          <p style={{ color: "var(--color-fail)" }}>{error}</p>
        </div>
      )}

      {!loading && diagnostics.length > 0 && (
        <>
          <div className="domain-chips" style={{ marginBottom: "var(--space-6)" }}>
            {counts.ok > 0 && (
              <span className="domain-chip status-ok">{counts.ok} OK</span>
            )}
            {counts.warn > 0 && (
              <span className="domain-chip status-warn">{counts.warn} WARN</span>
            )}
            {counts.fail > 0 && (
              <span className="domain-chip status-fail">{counts.fail} FAIL</span>
            )}
          </div>

          <div className="card">
            <table className="diag-table" role="table">
              <thead>
                <tr>
                  <th scope="col">Service</th>
                  <th scope="col">Status</th>
                  <th scope="col">Details</th>
                </tr>
              </thead>
              <tbody>
                {diagnostics.map((d, i) => {
                  const status = STATUS_LABELS[d.status] || { text: d.status, className: "" };
                  return (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{d.name}</td>
                      <td>
                        <span className={status.className}>{status.text}</span>
                      </td>
                      <td style={{ color: "var(--color-text-secondary)" }}>{d.message}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {loading && (
        <div className="response-area loading">
          <div className="spinner" />
        </div>
      )}
    </div>
  );
}
