import "./App.css";

function App() {
  return (
    <main className="app">
      <section className="hero">
        <p className="eyebrow">CaptUReFraud</p>
        <h1>Fraud Monitoring Dashboard</h1>
        <p className="heroText">
          Frontend interface for fraud prediction, transaction simulation,
          threshold experimentation, and analyst decision support.
        </p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>API Status</h2>
          <p className="statusBadge">Not connected yet</p>
          <p>
            This section will display backend health and runtime metadata from
            the FastAPI service.
          </p>
        </article>

        <article className="card">
          <h2>Transaction Simulation</h2>
          <p>
            This section will display simulated transaction batches with model
            prediction, fraud probability, decision, and outcome.
          </p>
        </article>

        <article className="card">
          <h2>Business Metrics</h2>
          <p>
            This section will display fraud recall, missed frauds, blocked
            legitimate transactions, and estimated business costs.
          </p>
        </article>
      </section>
    </main>
  );
}

export default App;