
export default function MatchingPage() {
  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">INTELLIGENT SCREENING</p>
          <h1>Candidate Matching</h1>
          <p className="welcome-description">
            Compare candidate resumes against job requirements and understand
            how closely they align.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-caption">MATCHES</span>
          <h2>0</h2>
          <p>Total comparisons</p>
        </div>
        <div className="stat-card">
          <span className="stat-caption">CANDIDATES</span>
          <h2>0</h2>
          <p>Available resumes</p>
        </div>
        <div className="stat-card">
          <span className="stat-caption">POSITIONS</span>
          <h2>0</h2>
          <p>Available jobs</p>
        </div>
      </section>

      <section className="activity-section">
        <h2>Start a comparison</h2>
        <div className="empty-state">
          <h3>Ready to find a match?</h3>
          <p>
            Once resumes and job descriptions are uploaded, you can compare
            candidates using semantic scoring and structured requirement
            analysis.
          </p>
        </div>
      </section>
    </div>
  );
}
