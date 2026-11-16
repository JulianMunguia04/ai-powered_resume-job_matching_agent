
export default function ResumesPage() {
  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">CANDIDATE MANAGEMENT</p>
          <h1>Resumes</h1>
          <p className="welcome-description">
            Upload, organize, and analyze candidate resumes.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-caption">TOTAL RESUMES</span>
          <h2>0</h2>
          <p>Stored candidates</p>
        </div>
        <div className="stat-card">
          <span className="stat-caption">ANALYZED</span>
          <h2>0</h2>
          <p>Completed analyses</p>
        </div>
        <div className="stat-card">
          <span className="stat-caption">PENDING</span>
          <h2>0</h2>
          <p>Awaiting analysis</p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>All resumes</h2>
            <p>Your uploaded candidate documents will appear here.</p>
          </div>
        </div>

        <div className="empty-state">
          <h3>No resumes uploaded</h3>
          <p>
            Use the Upload document button above to add your first candidate
            resume.
          </p>
        </div>
      </section>
    </div>
  );
}
