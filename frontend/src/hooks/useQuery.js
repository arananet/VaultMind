import { useState, useCallback } from "react";

/**
 * Custom hook for querying the VaultMind API.
 * Handles loading state, errors, and response data.
 */
export function useVaultQuery() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const query = useCallback(async (queryText) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { query, loading, error, result, reset };
}

/**
 * Fetch available knowledge guide domains.
 */
export async function fetchGuides() {
  const response = await fetch("/api/guides");
  if (!response.ok) throw new Error("Failed to load guides");
  return response.json();
}

/**
 * Fetch guide content for a specific domain.
 */
export async function fetchGuideContent(domain) {
  const response = await fetch(`/api/guides/${domain}`);
  if (!response.ok) throw new Error(`Failed to load guide: ${domain}`);
  return response.json();
}

/**
 * Fetch system diagnostics.
 */
export async function fetchDiagnostics() {
  const response = await fetch("/api/status");
  if (!response.ok) throw new Error("Failed to load diagnostics");
  return response.json();
}

/**
 * Request TTS synthesis for text.
 */
export async function synthesizeSpeech(text) {
  const response = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) throw new Error("TTS synthesis failed");
  return response.blob();
}
