import { useEffect, useState } from "react";
import "./App.css";
import {
  fetchBatchSimulation,
  fetchHealth,
  fetchMetadata,
  fetchPredictionSample,
  fetchSimulationMetrics,
  getApiBaseUrl,
} from "./api/client";

const DEFAULT_LIMIT = 5;
const DEFAULT_THRESHOLD = 0.8;

function App() {
  const [health, setHealth] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const [isSystemLoading, setIsSystemLoading] = useState(true);
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadSystemData() {
      setIsSystemLoading(true);
      setErrorMessage("");

      try {
        const [healthResponse, metadataResponse] = await Promise.all([
          fetchHealth(),
          fetchMetadata(),
        ]);

        setHealth(healthResponse);
        setMetadata(metadataResponse);
      } catch (error) {
        setErrorMessage(error.message || "Failed to load system API data.");
      } finally {
        setIsSystemLoading(false);
      }
    }

    loadSystemData();
  }, []);

  async function loadDashboardData() {
    setIsDashboardLoading(true);
    setErrorMessage("");

    try {
      const predictionResponse = await fetchPredictionSample();
      setPrediction(predictionResponse);

      const simulationResponse = await fetchBatchSimulation({
        limit: DEFAULT_LIMIT,
        threshold: DEFAULT_THRESHOLD,
      });
      setSimulation(simulationResponse);

      const metricsResponse = await fetchSimulationMetrics({
        threshold: DEFAULT_THRESHOLD,
      });
      setMetrics(metricsResponse);
    } catch (error) {
      setErrorMessage(error.message || "Failed to load dashboard data.");
    } finally {
      setIsDashboardLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <p className="eyebrow">CaptUReFraud</p>
        <h1>Fraud Monitoring Dashboard</h1>
        <p className="heroText">
          Frontend interface connected to the FastAPI backend for fraud
          prediction, batch simulation, and business metrics.
        </p>
        <p className="apiUrl">API base URL: {getApiBaseUrl()}</p>

        <button
          className="primaryButton"
          type="button"
          onClick={loadDashboardData}
          disabled={isDashboardLoading}
        >
          {isDashboardLoading ? "Loading API data..." : "Load API data"}
        </button>
      </section>

      {isSystemLoading && (
        <section className="notice loading">
          Loading system status from backend API...
        </section>
      )}

      {errorMessage && (
        <section className="notice error">
          <strong>API error:</strong> {errorMessage}
        </section>
      )}

      <section className="grid">
        <article className="card">
          <h2>API Status</h2>
          <p className={health?.status === "ok" ? "statusBadge online" : "statusBadge"}>
            {health?.status === "ok" ? "API Online" : "Not connected"}
          </p>

          {metadata ? (
            <dl className="details">
              <div>
                <dt>Project</dt>
                <dd>{metadata.project}</dd>
              </div>
              <div>
                <dt>API version</dt>
                <dd>{metadata.api_version}</dd>
              </div>
              <div>
                <dt>Model</dt>
                <dd>{metadata.model_type}</dd>
              </div>
              <div>
                <dt>Runtime</dt>
                <dd>{metadata.runtime}</dd>
              </div>
            </dl>
          ) : (
            <p>Backend metadata will be displayed here.</p>
          )}
        </article>

        <article className="card">
          <h2>Sample Prediction</h2>

          {prediction ? (
            <dl className="details">
              <div>
                <dt>Prediction</dt>
                <dd>{prediction.prediction}</dd>
              </div>
              <div>
                <dt>Fraud probability</dt>
                <dd>{formatPercent(prediction.fraud_probability)}</dd>
              </div>
              <div>
                <dt>Threshold</dt>
                <dd>{prediction.threshold}</dd>
              </div>
            </dl>
          ) : (
            <p>Click Load API data to fetch a sample prediction.</p>
          )}
        </article>

        <article className="card">
          <h2>Business Metrics</h2>

          {metrics ? (
            <dl className="details">
              <div>
                <dt>Total transactions</dt>
                <dd>{metrics.total_transactions}</dd>
              </div>
              <div>
                <dt>Fraud recall</dt>
                <dd>{formatPercent(metrics.fraud_recall)}</dd>
              </div>
              <div>
                <dt>Missed frauds</dt>
                <dd>{metrics.missed_frauds}</dd>
              </div>
              <div>
                <dt>Total cost</dt>
                <dd>{formatCurrency(metrics.estimated_total_cost)}</dd>
              </div>
            </dl>
          ) : (
            <p>Click Load API data to fetch business metrics.</p>
          )}
        </article>
      </section>

      <section className="card tableCard">
        <div className="sectionHeader">
          <h2>Batch Simulation Preview</h2>
          <p>
            Showing first {simulation?.count ?? DEFAULT_LIMIT} records at
            threshold {simulation?.threshold ?? DEFAULT_THRESHOLD}.
          </p>
        </div>

        {simulation?.records?.length > 0 ? (
          <div className="tableWrapper">
            <table>
              <thead>
                <tr>
                  <th>Label</th>
                  <th>Prediction</th>
                  <th>Fraud probability</th>
                  <th>Decision</th>
                  <th>Outcome</th>
                </tr>
              </thead>
              <tbody>
                {simulation.records.map((record, index) => (
                  <tr key={`${record.label}-${record.prediction}-${index}`}>
                    <td>{record.label}</td>
                    <td>{record.prediction}</td>
                    <td>{formatPercent(record.fraud_probability)}</td>
                    <td>
                      <span className={`pill ${record.decision}`}>
                        {record.decision}
                      </span>
                    </td>
                    <td>
                      <span className={`pill outcome-${record.prediction_outcome}`}>
                        {record.prediction_outcome}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>Click Load API data to fetch simulation records.</p>
        )}
      </section>
    </main>
  );
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  return `${(Number(value) * 100).toFixed(2)}%`;
}

function formatCurrency(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

export default App;