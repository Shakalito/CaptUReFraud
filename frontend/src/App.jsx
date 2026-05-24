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
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD);
  const [pendingThreshold, setPendingThreshold] = useState(DEFAULT_THRESHOLD);

  const [selectedTransactionIndex, setSelectedTransactionIndex] = useState(null);
  const [analystDecisions, setAnalystDecisions] = useState({});

  const [isSystemLoading, setIsSystemLoading] = useState(true);
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const selectedTransaction =
    selectedTransactionIndex !== null
      ? simulation?.records?.[selectedTransactionIndex]
      : null;

  const selectedAnalystDecision =
    selectedTransactionIndex !== null
      ? analystDecisions[selectedTransactionIndex]
      : null;

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

  async function loadDashboardData({
    customLimit = batchSize,
    customThreshold = threshold,
  } = {}) {
    setIsDashboardLoading(true);
    setErrorMessage("");

    try {
      const predictionResponse = await fetchPredictionSample();
      setPrediction(predictionResponse);

      const simulationResponse = await fetchBatchSimulation({
        limit: customLimit,
        threshold: customThreshold,
      });
      setSimulation(simulationResponse);

      const metricsResponse = await fetchSimulationMetrics({
        threshold: customThreshold,
      });
      setMetrics(metricsResponse);

      setSelectedTransactionIndex(null);
      setAnalystDecisions({});
    } catch (error) {
      setErrorMessage(error.message || "Failed to load dashboard data.");
    } finally {
      setIsDashboardLoading(false);
    }
  }

  function handleBatchSizeChange(event) {
    setBatchSize(Number(event.target.value));
  }

  function handleThresholdChange(event) {
    setPendingThreshold(Number(event.target.value));
  }

  function applyThreshold() {
    setThreshold(pendingThreshold);
    loadDashboardData({
      customLimit: batchSize,
      customThreshold: pendingThreshold,
    });
  }

  function resetThreshold() {
    setPendingThreshold(DEFAULT_THRESHOLD);
    setThreshold(DEFAULT_THRESHOLD);
    loadDashboardData({
      customLimit: batchSize,
      customThreshold: DEFAULT_THRESHOLD,
    });
  }

  function handleLoadBatch() {
    loadDashboardData({
      customLimit: batchSize,
      customThreshold: threshold,
    });
  }

  function selectTransaction(index) {
    setSelectedTransactionIndex(index);
  }

  function setAnalystDecision(decision) {
    if (selectedTransactionIndex === null) {
      return;
    }

    setAnalystDecisions((currentDecisions) => ({
      ...currentDecisions,
      [selectedTransactionIndex]: decision,
    }));
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
          <span>Applied threshold</span>
          <strong>{threshold.toFixed(2)}</strong>
        </div>
      </section>

      <section className="thresholdPanel">
        <div>
          <p className="eyebrow">Threshold experiment</p>
          <h2>Decision threshold</h2>
          <p>
            Lower threshold usually detects more fraud but may block more
            legitimate transactions. Higher threshold usually reduces false
            positives but may miss more fraud.
          </p>
        </div>

        <div className="thresholdControls">
          <div className="thresholdValue">
            <span>Selected threshold</span>
            <strong>{pendingThreshold.toFixed(2)}</strong>
          </div>

          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={pendingThreshold}
            onChange={handleThresholdChange}
            disabled={isDashboardLoading}
          />

          <div className="thresholdScale">
            <span>0.00</span>
            <span>0.50</span>
            <span>1.00</span>
          </div>

          <div className="thresholdButtons">
            <button
              className="primaryButton"
              type="button"
              onClick={applyThreshold}
              disabled={isDashboardLoading}
            >
              Apply threshold
            </button>

            <button
              className="secondaryButton"
              type="button"
              onClick={resetThreshold}
              disabled={isDashboardLoading}
            >
              Reset to 0.80
            </button>
          </div>
        </div>
      </section>

      <section className="metricsGrid six">
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
          label="Fraud loss"
          value={metrics ? formatCurrency(metrics.estimated_fraud_loss) : "-"}
        />
        <MetricCard
          label="Blocking cost"
          value={metrics ? formatCurrency(metrics.estimated_blocking_cost) : "-"}
        />
        <MetricCard
          label="Total cost"
          value={metrics ? formatCurrency(metrics.estimated_total_cost) : "-"}
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
                <dt>Prediction threshold</dt>
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

      <section className="visualGrid">
        <article className="card">
          <h2>Cost Breakdown</h2>
          {metrics ? (
            <div className="barChart">
              <CostBar
                label="Fraud loss"
                value={metrics.estimated_fraud_loss}
                total={metrics.estimated_total_cost}
              />
              <CostBar
                label="Blocking cost"
                value={metrics.estimated_blocking_cost}
                total={metrics.estimated_total_cost}
              />
            </div>
          ) : (
            <p>Load API data to display estimated cost breakdown.</p>
          )}
        </article>

        <article className="card">
          <h2>Decision Trade-off</h2>
          {metrics ? (
            <div className="barChart">
              <CountBar
                label="Missed frauds"
                value={metrics.missed_frauds}
                total={
                  metrics.missed_frauds +
                  metrics.blocked_legit_transactions
                }
              />
              <CountBar
                label="Blocked legitimate"
                value={metrics.blocked_legit_transactions}
                total={
                  metrics.missed_frauds +
                  metrics.blocked_legit_transactions
                }
              />
            </div>
          ) : (
            <p>Load API data to display decision trade-off.</p>
          )}
        </article>
      </section>

      <section className="workflowGrid">
        <section className="card tableCard">
          <div className="sectionHeader">
            <div>
              <h2>Transaction Simulation Records</h2>
              <p>
                Select a transaction to review model output and make an analyst
                decision.
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
                    <th>System decision</th>
                    <th>Outcome</th>
                    <th>Analyst decision</th>
                  </tr>
                </thead>
                <tbody>
                  {simulation.records.map((record, index) => (
                    <tr
                      key={`${record.label}-${record.prediction}-${index}`}
                      className={
                        selectedTransactionIndex === index ? "selectedRow" : ""
                      }
                      onClick={() => selectTransaction(index)}
                    >
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
                      <td>
                        {analystDecisions[index] ? (
                          <span className={`pill ${analystDecisions[index]}`}>
                            {analystDecisions[index]}
                          </span>
                        ) : (
                          <span className="mutedText">Not reviewed</span>
                        )}
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

        <aside className="card analystPanel">
          <h2>Analyst Review</h2>

          {selectedTransaction ? (
            <>
              <p className="panelIntro">
                Review selected transaction and confirm the analyst-facing
                decision. This is stored only in frontend state.
              </p>

              <dl className="details">
                <div>
                  <dt>Selected row</dt>
                  <dd>{selectedTransactionIndex + 1}</dd>
                </div>
                <div>
                  <dt>True label</dt>
                  <dd>{formatLabel(selectedTransaction.label)}</dd>
                </div>
                <div>
                  <dt>Model prediction</dt>
                  <dd>{formatPrediction(selectedTransaction.prediction)}</dd>
                </div>
                <div>
                  <dt>Fraud probability</dt>
                  <dd>{formatPercent(selectedTransaction.fraud_probability)}</dd>
                </div>
                <div>
                  <dt>System decision</dt>
                  <dd>
                    <span className={`pill ${selectedTransaction.decision}`}>
                      {selectedTransaction.decision}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Prediction outcome</dt>
                  <dd>
                    <span
                      className={`pill outcome-${selectedTransaction.prediction_outcome}`}
                    >
                      {selectedTransaction.prediction_outcome}
                    </span>
                  </dd>
                </div>
              </dl>

              <div className="analystActions">
                <button
                  type="button"
                  className="decisionButton allowButton"
                  onClick={() => setAnalystDecision("allow")}
                >
                  Mark allow
                </button>
                <button
                  type="button"
                  className="decisionButton blockButton"
                  onClick={() => setAnalystDecision("block")}
                >
                  Mark block
                </button>
              </div>

              {selectedAnalystDecision ? (
                <AnalystDecisionFeedback
                  transaction={selectedTransaction}
                  decision={selectedAnalystDecision}
                />
              ) : (
                <p className="mutedText">
                  No analyst decision selected yet.
                </p>
              )}
            </>
          ) : (
            <p>
              Select a transaction from the table to review model output and
              choose an analyst decision.
            </p>
          )}
        </aside>
      </section>
    </main>
  );
}

function AnalystDecisionFeedback({ transaction, decision }) {
  const expectedDecision = getExpectedDecision(transaction.label);
  const isCorrect = decision === expectedDecision;

  return (
    <div className={isCorrect ? "feedbackBox success" : "feedbackBox danger"}>
      <strong>
        {isCorrect ? "Decision aligns with label" : "Decision conflicts with label"}
      </strong>
      <p>
        Analyst selected <strong>{decision}</strong>. Based on the known label,
        expected decision is <strong>{expectedDecision}</strong>.
      </p>
    </div>
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

function CostBar({ label, value, total }) {
  const width = total > 0 ? Math.max((Number(value) / Number(total)) * 100, 2) : 0;

  return (
    <div className="barRow">
      <div className="barMeta">
        <span>{label}</span>
        <strong>{formatCurrency(value)}</strong>
      </div>
      <div className="chartTrack">
        <div className="chartFill" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

function CountBar({ label, value, total }) {
  const width = total > 0 ? Math.max((Number(value) / Number(total)) * 100, 2) : 0;

  return (
    <div className="barRow">
      <div className="barMeta">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <div className="chartTrack">
        <div className="chartFill warning" style={{ width: `${width}%` }} />
      </div>
    </div>
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

function getExpectedDecision(label) {
  return Number(label) === 1 ? "block" : "allow";
}

export default App;