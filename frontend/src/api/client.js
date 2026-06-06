const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function requestJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const errorPayload = await response.json();

      if (errorPayload.error && errorPayload.detail) {
        message = `${errorPayload.error}: ${errorPayload.detail}`;
      } else if (Array.isArray(errorPayload.detail)) {
        message = errorPayload.detail
          .map((item) => item.msg || JSON.stringify(item))
          .join("; ");
      } else if (errorPayload.detail) {
        message = errorPayload.detail;
      }
    } catch {
      // Keep default message if response body is not JSON.
    }

    throw new Error(message);
  }

  return response.json();
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function fetchHealth() {
  return requestJson("/health");
}

export function fetchMetadata() {
  return requestJson("/metadata");
}

export function fetchPredictionSample() {
  return requestJson("/prediction/sample");
}

export function fetchBatchSimulation({ limit = 5, threshold = 0.8 } = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    threshold: String(threshold),
  });

  return requestJson(`/simulation/batch?${params.toString()}`);
}

export function fetchSimulationMetrics({ threshold = 0.8 } = {}) {
  const params = new URLSearchParams({
    threshold: String(threshold),
  });

  return requestJson(`/simulation/metrics?${params.toString()}`);
}

export function fetchEvaluationMetrics({ threshold = 0.8 } = {}) {
  const params = new URLSearchParams({
    threshold: String(threshold),
  });

  return requestJson(`/evaluation/model?${params.toString()}`);
}
