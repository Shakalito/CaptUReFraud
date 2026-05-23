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

const DEFAULT_LIMIT = 10;
const DEFAULT_THRESHOLD = 0.8;

function App() {
  const [health, setHealth] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const [batchSize, setBatchSize] = useState(DEFAULT_LIMIT);
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

  async function loadDashboardData(customLimit = batchSize) {
    setIsDashboardLoading(true);
    setErrorMessage("");

    try {
      const predictionResponse = await fetchPredictionSample();
      setPrediction(predictionResponse);

      const simulationResponse = await fetchBatchSimulation({
        limit: customLimit,
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

  function handleBatchSizeChange(event) {
    setBatchSize(Number(event.target.value));
  }

  function handleLoadBatch() {
    loadDashboardData(batchSize);
  }

  return (
    <main className="app">
      <section className="hero">
        <div>
          <p className="eyebrow">CaptUReFraud</p>
          <h1>Fraud Monitoring Dashboard</h1>
          <p className="heroText">
            Analyst-oriented view for model prediction, transaction simulation,
            decision outcomes, and business-level fraud monitoring.
          </p>
          <p className="apiUrl">API base URL: {getApiBaseUrl()}</p>
        </div>

        <div className="heroActions">
          <label className="controlLabel" htmlFor="batchSize">
            Batch size
          </label>
          <select
            id="batchSize"
            value={batchSize}
            onChange={handleBatchSizeChange}
            disabled={isDashboardLoading}
          >
            <option value={5}>5 records</option>
            <option value={10}>10 records</option>
            <option value={25}>25 records</option>
            <option value={50}>50 records</option>
            <option value={100}>100 records</option>
          </select>

          <button
            className="primaryButton"
            type="button"
            onClick={handleLoadBatch}
            disabled={isDashboardLoading}
          >
            {isDashboardLoading ? "Loading..." : "Load / refresh batch"}
          </button>
        </div>
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

      <section className="statusBar">
        <div className="statusItem">
          <span>API status</span>
          <strong className={health?.status === "ok" ? "textSuccess" : "textMuted"}>
            {health?.status === "ok" ? "Online" : "Unknown"}
          </strong>
        </div>

        <div className="statusItem">
          <span>API version</span>
          <strong>{metadata?.api_version ?? "-"}</strong>
        </div>

        <div className="statusItem">
          <span>Model</span>
          <strong>{metadata?.model_type ?? "-"}</strong>
        </div>

        <div className="statusItem">
          <span>Threshold</span>
          <strong>{DEFAULT_THRESHOLD}</strong>
        </div>
      </section>

      <section className="metricsGrid">
        <MetricCard
          label="Fraud recall"
          value={metrics ? formatPercent(metrics.fraud_recall) : "-"}
        />
        <MetricCard
          label="Missed frauds"
          value={metrics?.missed_frauds ?? "-"}
        />
        <MetricCard
          label="Blocked legitimate"
          value={metrics?.blocked_legit_transactions ?? "-"}
        />
        <MetricCard
          label="Estimated total cost"
          value={
            metrics ? formatCurrency(metrics.estimated_total_cost) : "-"
          }
        />
      </section>

      <section className="grid">
        <article className="card">
          <h2>Sample Prediction</h2>

          {prediction ? (
            <dl className="details">
              <div>
                <dt>Prediction</dt>
                <dd>{formatPrediction(prediction.prediction)}</dd>
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
            <p>Click Load / refresh batch to fetch a sample prediction.</p>
          )}
        </article>

        <article className="card">
          <h2>Simulation Summary</h2>

          {simulation ? (
            <dl className="details">
              <div>
                <dt>Displayed records</dt>
                <dd>{simulation.count}</dd>
              </div>
              <div>
                <dt>Requested batch size</dt>
                <dd>{batchSize}</dd>
              </div>
              <div>
                <dt>Decision threshold</dt>
                <dd>{simulation.threshold}</dd>
              </div>
            </dl>
          ) : (
            <p>Simulation summary will appear after loading API data.</p>
          )}
        </article>

        <article className="card">
          <h2>Outcome Legend</h2>
          <div className="legend">
            <span className="pill outcome-TP">TP</span>
            <span>Fraud correctly detected</span>
          </div>
          <div className="legend">
            <span className="pill outcome-FP">FP</span>
            <span>Legitimate transaction predicted as fraud</span>
          </div>
          <div className="legend">
            <span className="pill outcome-TN">TN</span>
            <span>Legitimate transaction correctly allowed</span>
          </div>
          <div className="legend">
            <span className="pill outcome-FN">FN</span>
            <span>Fraud missed by model</span>
          </div>
        </article>
      </section>

      <section className="card tableCard">
        <div className="sectionHeader">
          <div>
            <h2>Transaction Simulation Records</h2>
            <p>
              Simulated transaction results with model prediction, fraud
              probability, operational decision, and prediction outcome.
            </p>
          </div>
          <button
            className="secondaryButton"
            type="button"
            onClick={handleLoadBatch}
            disabled={isDashboardLoading}
          >
            Refresh
          </button>
        </div>

        {simulation?.records?.length > 0 ? (
          <div className="tableWrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>True label</th>
                  <th>Prediction</th>
                  <th>Fraud probability</th>
                  <th>Decision</th>
                  <th>Outcome</th>
                </tr>
              </thead>
              <tbody>
                {simulation.records.map((record, index) => (
                  <tr key={`${record.label}-${record.prediction}-${index}`}>
                    <td>{index + 1}</td>
                    <td>{formatLabel(record.label)}</td>
                    <td>{formatPrediction(record.prediction)}</td>
                    <td>
                      <div className="probabilityCell">
                        <span>{formatPercent(record.fraud_probability)}</span>
                        <div className="probabilityTrack">
                          <div
                            className="probabilityFill"
                            style={{
                              width: `${Math.min(
                                Number(record.fraud_probability) * 100,
                                100
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    </td>
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
          <p>Click Load / refresh batch to fetch simulation records.</p>
        )}
      </section>
    </main>
  );
}

function MetricCard({ label, value }) {
  return (
    <article className="metricCard">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
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

function formatLabel(value) {
  return Number(value) === 1 ? "Fraud" : "Legit";
}

function formatPrediction(value) {
  return Number(value) === 1 ? "Fraud" : "Legit";
}

export default App;