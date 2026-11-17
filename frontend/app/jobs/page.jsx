
"use client";

import { useCallback, useEffect, useState } from "react";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchJobs = useCallback(async () => {
    try {
      const response = await fetch("/api/jobs", {
        cache: "no-store"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to load jobs.");
      }

      setJobs(data.jobs || []);
      setTotal(data.total ?? data.jobs?.length ?? 0);
      setError("");

    } catch (err) {
      console.error("Jobs loading error:", err);
      setError(err.message || "Unable to load job descriptions.");

    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();

    window.addEventListener("workspace-data-updated", fetchJobs);

    return () => {
      window.removeEventListener("workspace-data-updated", fetchJobs);
    };
  }, [fetchJobs]);

  const analyzedCount = jobs.filter(
    (job) => job.is_analyzed
  ).length;

  const pendingCount = total - analyzedCount;

  function formatDate(date) {
    if (!date) return "Date unavailable";

    return new Date(date).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric"
    });
  }

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
          <h2>{loading ? "..." : total}</h2>
          <p>Stored job descriptions</p>
        </div>

        <div className="stat-card">
          <span className="stat-caption">ANALYZED</span>
          <h2>{loading ? "..." : analyzedCount}</h2>
          <p>Completed analyses</p>
        </div>

        <div className="stat-card">
          <span className="stat-caption">PENDING</span>
          <h2>{loading ? "..." : pendingCount}</h2>
          <p>Awaiting analysis</p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>All job descriptions</h2>
            <p>
              {loading
                ? "Loading your stored positions..."
                : `${total} job description${total === 1 ? "" : "s"} stored`}
            </p>
          </div>
        </div>

        {error ? (
          <div className="empty-state">
            <h3>Unable to load job descriptions</h3>
            <p>{error}</p>
            <button onClick={fetchJobs}>Try again</button>
          </div>
        ) : loading ? (
          <div className="empty-state">
            <p>Loading job descriptions...</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <h3>No job descriptions yet</h3>
            <p>
              Upload a job description to begin extracting requirements and
              qualifications.
            </p>
          </div>
        ) : (
          <div className="document-list">
            {jobs.map((job) => (
              <article className="document-card" key={job.id}>
                <div className="document-card-header">
                  <div>
                    <h3>{job.title}</h3>
                    <p>Added {formatDate(job.created_at)}</p>
                  </div>

                  <span className={`document-status ${
                    job.is_analyzed ? "success" : "pending"
                  }`}>
                    {job.is_analyzed ? "Analyzed" : "Pending"}
                  </span>
                </div>

                <p className="document-description">
                  {job.description}
                </p>

                <span className="document-id">
                  ID: {job.id}
                </span>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
