
export default function JobsPage() {
  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">POSITION MANAGEMENT</p>
          <h1>Job Descriptions</h1>
          <p className="welcome-description">
            Manage job postings and analyze their required qualifications.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-caption">TOTAL POSITIONS</span>
          <h2>0</h2>
          <p>Stored job descriptions</p>
        </div>
        <div className="stat-card">
          <span className="stat-caption">ANALYZED</span>
          <h2>0</h2>
          <p>Completed analyses</p>
        </div>
        <div className="stat-card">
          <span className="stat-caption">REQUIREMENTS</span>
          <h2>0</h2>
          <p>Positions analyzed</p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>All job descriptions</h2>
            <p>Your stored positions will appear here.</p>
          </div>
        </div>

        <div className="empty-state">
          <h3>No job descriptions yet</h3>
          <p>
            Upload a job description to begin extracting requirements and
            qualifications.
          </p>
        </div>
      </section>
    </div>
  );
}
