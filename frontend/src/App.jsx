import { useEffect, useMemo, useState } from "react";
import "./App.css";
import {
  fetchBatchSimulation,
  fetchEvaluationMetrics,
  fetchHealth,
  fetchMetadata,
  fetchSimulationMetrics,
  getApiBaseUrl,
} from "./api/client";

const DEFAULT_LIMIT = 10;
const DEFAULT_THRESHOLD = 0.8;

function App() {
  const [health, setHealth] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [evaluationMetrics, setEvaluationMetrics] = useState(null);

  const [batchSize, setBatchSize] = useState(DEFAULT_LIMIT);
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD);
  const [pendingThreshold, setPendingThreshold] = useState(DEFAULT_THRESHOLD);

  const [selectedTransactionIndex, setSelectedTransactionIndex] = useState(null);
  const [analystDecisions, setAnalystDecisions] = useState({});
  const [isEvaluationRevealed, setIsEvaluationRevealed] = useState(false);

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

  const analystSummary = useMemo(
    () => calculateAnalystSummary(simulation?.records ?? [], analystDecisions),
    [simulation, analystDecisions]
  );

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
      const simulationResponse = await fetchBatchSimulation({
        limit: customLimit,
        threshold: customThreshold,
      });
      setSimulation(simulationResponse);

      const metricsResponse = await fetchSimulationMetrics({
        threshold: customThreshold,
      });
      setMetrics(metricsResponse);

      const evaluationResponse = await fetchEvaluationMetrics({
        threshold: customThreshold,
      });
      setEvaluationMetrics(evaluationResponse);

      setSelectedTransactionIndex(null);
      setAnalystDecisions({});
      setIsEvaluationRevealed(false);
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

  function evaluateDecisions() {
    setIsEvaluationRevealed(true);
  }

  function resetAnalystReview() {
    setAnalystDecisions({});
    setSelectedTransactionIndex(null);
    setIsEvaluationRevealed(false);
  }

  return (
    <main className="app">
      <section className="hero">
        <div>
          <p className="eyebrow">CaptUReFraud</p>
          <h1>Fraud Monitoring Dashboard</h1>
          <p className="heroText">
            Review simulated transactions, compare model recommendations, adjust
            the fraud threshold, and evaluate analyst decisions after revealing
            known outcomes.
          </p>
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

      <section className="topInfoGrid">
        <section className="workflowSteps">
          <div className="workflowStep">
            <span>1</span>
            <div>
              <strong>Load transactions</strong>
              <p>Fetch a simulated batch from the backend.</p>
            </div>
          </div>

          <div className="workflowStep">
            <span>2</span>
            <div>
              <strong>Review decisions</strong>
              <p>Select transactions and mark allow or block.</p>
            </div>
          </div>

          <div className="workflowStep">
            <span>3</span>
            <div>
              <strong>Evaluate results</strong>
              <p>Reveal known labels and measure analyst performance.</p>
            </div>
          </div>
        </section>

        <section className="compactStatusBar">
          <div className="compactStatusMain">
            <span
              className={
                health?.status === "ok"
                  ? "statusDot online"
                  : "statusDot offline"
              }
            />
            <strong>
              {health?.status === "ok"
                ? "System online"
                : "System status unknown"}
            </strong>
            <span>Threshold {threshold.toFixed(2)}</span>
            <span>Batch size {batchSize}</span>
          </div>

          <details className="technicalDetails">
            <summary>Technical details</summary>
            <dl>
              <div>
                <dt>API base URL</dt>
                <dd>{getApiBaseUrl()}</dd>
              </div>
              <div>
                <dt>API version</dt>
                <dd>{metadata?.api_version ?? "-"}</dd>
              </div>
              <div>
                <dt>Model</dt>
                <dd>{metadata?.model_type ?? "-"}</dd>
              </div>
              <div>
                <dt>Runtime</dt>
                <dd>{metadata?.runtime ?? "-"}</dd>
              </div>
            </dl>
          </details>
        </section>
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

      <section className="evaluationSection">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Evaluation</p>
            <h2>Model decision quality</h2>
            <p>
              Evaluation metrics show how threshold-based system decisions perform
              against known labels. This section explains false positives, false
              negatives, and the precision-recall trade-off.
            </p>
          </div>
        </div>

        {evaluationMetrics ? (
          <>
            <section className="metricsGrid five">
              <MetricCard
                label="Precision"
                value={formatPercent(evaluationMetrics.precision)}
              />
              <MetricCard
                label="Recall"
                value={formatPercent(evaluationMetrics.recall)}
              />
              <MetricCard
                label="F1 score"
                value={formatPercent(evaluationMetrics.f1_score)}
              />
              <MetricCard
                label="False positive rate"
                value={formatPercent(evaluationMetrics.false_positive_rate)}
              />
              <MetricCard
                label="False negative rate"
                value={formatPercent(evaluationMetrics.false_negative_rate)}
              />
            </section>

            <section className="evaluationGrid">
              <article className="card">
                <h2>Confusion Matrix</h2>
                <div className="confusionMatrix">
                  <div className="confusionCell success">
                    <span>True Positive</span>
                    <strong>{evaluationMetrics.true_positives}</strong>
                    <p>Fraud correctly blocked</p>
                  </div>

                  <div className="confusionCell warning">
                    <span>False Positive</span>
                    <strong>{evaluationMetrics.false_positives}</strong>
                    <p>Legitimate transaction incorrectly blocked</p>
                  </div>

                  <div className="confusionCell neutral">
                    <span>True Negative</span>
                    <strong>{evaluationMetrics.true_negatives}</strong>
                    <p>Legitimate transaction correctly allowed</p>
                  </div>

                  <div className="confusionCell danger">
                    <span>False Negative</span>
                    <strong>{evaluationMetrics.false_negatives}</strong>
                    <p>Fraud transaction missed</p>
                  </div>
                </div>
              </article>

              <article className="card">
                <h2>Error Interpretation</h2>
                <div className="barChart">
                  <CountBar
                    label="False positives"
                    value={evaluationMetrics.false_positives}
                    total={
                      evaluationMetrics.false_positives +
                      evaluationMetrics.false_negatives
                    }
                  />
                  <CountBar
                    label="False negatives"
                    value={evaluationMetrics.false_negatives}
                    total={
                      evaluationMetrics.false_positives +
                      evaluationMetrics.false_negatives
                    }
                  />
                </div>

                <div className="interpretationList">
                  <p>
                    <strong>False positive:</strong> a legitimate transaction is
                    blocked or flagged as fraud.
                  </p>
                  <p>
                    <strong>False negative:</strong> a fraud transaction is allowed
                    and missed by the system.
                  </p>
                </div>
              </article>
            </section>
          </>
        ) : (
          <article className="card">
            <p>Load a simulation batch to display evaluation metrics.</p>
          </article>
        )}
      </section>

      {isEvaluationRevealed && (
        <section className="metricsGrid six">
          <MetricCard
            label="Reviewed"
            value={analystSummary.reviewedTransactions}
          />
          <MetricCard label="Correct" value={analystSummary.correctDecisions} />
          <MetricCard
            label="Incorrect"
            value={analystSummary.incorrectDecisions}
          />
          <MetricCard
            label="Analyst accuracy"
            value={formatPercent(analystSummary.accuracy)}
          />
          <MetricCard
            label="Frauds missed"
            value={analystSummary.fraudsMissedByAnalyst}
          />
          <MetricCard
            label="Legit blocked"
            value={analystSummary.legitBlockedByAnalyst}
          />
        </section>
      )}

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
                  metrics.missed_frauds + metrics.blocked_legit_transactions
                }
              />
              <CountBar
                label="Blocked legitimate"
                value={metrics.blocked_legit_transactions}
                total={
                  metrics.missed_frauds + metrics.blocked_legit_transactions
                }
              />
            </div>
          ) : (
            <p>Load API data to display decision trade-off.</p>
          )}
        </article>
      </section>

      <section className="reviewPanel">
        <div>
          <p className="eyebrow">Analyst simulation</p>
          <h2>Review transactions before revealing labels</h2>
          <p>
            Select transactions from the table, make allow/block decisions, and
            reveal known labels only when you are ready to evaluate analyst
            performance.
          </p>
        </div>

        <div className="reviewActions">
          <button
            className="primaryButton"
            type="button"
            onClick={evaluateDecisions}
            disabled={analystSummary.reviewedTransactions === 0}
          >
            Evaluate decisions
          </button>

          <button
            className="secondaryButton"
            type="button"
            onClick={resetAnalystReview}
            disabled={analystSummary.reviewedTransactions === 0}
          >
            Reset review
          </button>
        </div>
      </section>

      <section className="workflowGrid">
        <section className="card tableCard">
          <div className="sectionHeader">
            <div>
              <h2>Transaction Simulation Records</h2>
              <p>
                Select a transaction, review model output, and choose an analyst
                decision before revealing known labels.
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
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {simulation.records.map((record, index) => {
                    const analystDecision = analystDecisions[index];
                    const evaluation = analystDecision
                      ? getAnalystEvaluation(record, analystDecision)
                      : null;

                    return (
                      <tr
                        key={`${record.label}-${record.prediction}-${index}`}
                        className={
                          selectedTransactionIndex === index ? "selectedRow" : ""
                        }
                        onClick={() => selectTransaction(index)}
                      >
                        <td>{index + 1}</td>
                        <td>
                          {isEvaluationRevealed ? (
                            formatLabel(record.label)
                          ) : (
                            <span className="hiddenValue">Hidden</span>
                          )}
                        </td>
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
                          {isEvaluationRevealed ? (
                            <span
                              className={`pill outcome-${record.prediction_outcome}`}
                            >
                              {record.prediction_outcome}
                            </span>
                          ) : (
                            <span className="hiddenValue">Hidden</span>
                          )}
                        </td>
                        <td>
                          {analystDecision ? (
                            <span className={`pill ${analystDecision}`}>
                              {analystDecision}
                            </span>
                          ) : (
                            <span className="mutedText">Not reviewed</span>
                          )}
                        </td>
                        <td>
                          {isEvaluationRevealed && evaluation ? (
                            <span
                              className={
                                evaluation.isCorrect
                                  ? "resultBadge success"
                                  : "resultBadge danger"
                              }
                            >
                              {evaluation.isCorrect ? "Correct" : "Incorrect"}
                            </span>
                          ) : (
                            <span className="mutedText">Pending</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
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
                Review the model recommendation and choose an analyst decision.
                The known label is hidden until evaluation.
              </p>

              <dl className="details">
                <div>
                  <dt>Selected row</dt>
                  <dd>{selectedTransactionIndex + 1}</dd>
                </div>
                <div>
                  <dt>True label</dt>
                  <dd>
                    {isEvaluationRevealed ? (
                      formatLabel(selectedTransaction.label)
                    ) : (
                      <span className="hiddenValue">Hidden</span>
                    )}
                  </dd>
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
                    {isEvaluationRevealed ? (
                      <span
                        className={`pill outcome-${selectedTransaction.prediction_outcome}`}
                      >
                        {selectedTransaction.prediction_outcome}
                      </span>
                    ) : (
                      <span className="hiddenValue">Hidden</span>
                    )}
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
                <p>
                  Analyst decision:{" "}
                  <span className={`pill ${selectedAnalystDecision}`}>
                    {selectedAnalystDecision}
                  </span>
                </p>
              ) : (
                <p className="mutedText">No analyst decision selected yet.</p>
              )}

              {isEvaluationRevealed && selectedAnalystDecision && (
                <AnalystDecisionFeedback
                  transaction={selectedTransaction}
                  decision={selectedAnalystDecision}
                />
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
  const evaluation = getAnalystEvaluation(transaction, decision);

  return (
    <div
      className={
        evaluation.isCorrect ? "feedbackBox success" : "feedbackBox danger"
      }
    >
      <strong>
        {evaluation.isCorrect
          ? "Decision aligns with known label"
          : "Decision conflicts with known label"}
      </strong>
      <p>
        Analyst selected <strong>{decision}</strong>. Based on the known label,
        expected decision is <strong>{evaluation.expectedDecision}</strong>.
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
  const width =
    total > 0 ? Math.max((Number(value) / Number(total)) * 100, 2) : 0;

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
  const width =
    total > 0 ? Math.max((Number(value) / Number(total)) * 100, 2) : 0;

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

function calculateAnalystSummary(records, decisions) {
  const reviewedEntries = Object.entries(decisions).filter(
    ([index]) => records[Number(index)]
  );

  let correctDecisions = 0;
  let incorrectDecisions = 0;
  let fraudsMissedByAnalyst = 0;
  let legitBlockedByAnalyst = 0;

  reviewedEntries.forEach(([index, decision]) => {
    const record = records[Number(index)];
    const evaluation = getAnalystEvaluation(record, decision);

    if (evaluation.isCorrect) {
      correctDecisions += 1;
    } else {
      incorrectDecisions += 1;
    }

    if (Number(record.label) === 1 && decision === "allow") {
      fraudsMissedByAnalyst += 1;
    }

    if (Number(record.label) === 0 && decision === "block") {
      legitBlockedByAnalyst += 1;
    }
  });

  const reviewedTransactions = reviewedEntries.length;
  const accuracy =
    reviewedTransactions > 0 ? correctDecisions / reviewedTransactions : 0;

  return {
    reviewedTransactions,
    correctDecisions,
    incorrectDecisions,
    accuracy,
    fraudsMissedByAnalyst,
    legitBlockedByAnalyst,
  };
}

function getAnalystEvaluation(transaction, decision) {
  const expectedDecision = getExpectedDecision(transaction.label);

  return {
    expectedDecision,
    isCorrect: decision === expectedDecision,
  };
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