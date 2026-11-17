
"use client";

import { useCallback, useEffect, useState } from "react";

export default function ResumesPage() {
  const [resumes, setResumes] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchResumes = useCallback(async () => {
    try {
      const response = await fetch("/api/resumes", {
        cache: "no-store"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to load resumes.");
      }

      setResumes(data.resumes || []);
      setTotal(data.total ?? data.resumes?.length ?? 0);
      setError("");

    } catch (err) {
      console.error("Resumes loading error:", err);
      setError(err.message || "Unable to load resumes.");

    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResumes();

    window.addEventListener("workspace-data-updated", fetchResumes);

    return () => {
      window.removeEventListener("workspace-data-updated", fetchResumes);
    };
  }, [fetchResumes]);

  const analyzedCount = resumes.filter(
    (resume) => resume.is_analyzed
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
          <h2>{loading ? "..." : total}</h2>
          <p>Stored candidates</p>
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
            <h2>All resumes</h2>
            <p>
              {loading
                ? "Loading your candidate documents..."
                : `${total} resume${total === 1 ? "" : "s"} stored`}
            </p>
          </div>
        </div>

        {error ? (
          <div className="empty-state">
            <h3>Unable to load resumes</h3>
            <p>{error}</p>
            <button onClick={fetchResumes}>Try again</button>
          </div>
        ) : loading ? (
          <div className="empty-state">
            <p>Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <div className="empty-state">
            <h3>No resumes uploaded</h3>
            <p>
              Use the Upload document button above to add your first candidate
              resume.
            </p>
          </div>
        ) : (
          <div className="document-list">
            {resumes.map((resume) => (
              <article className="document-card mt-4" key={resume.id}>
                <div className="document-card-header">
                  <div>
                    <h3>Candidate Resume</h3>
                    <p>Added {formatDate(resume.created_at)}</p>
                  </div>

                  <span className={`document-status ${
                    resume.is_analyzed ? "success" : "pending"
                  }`}>
                    {resume.is_analyzed ? "Analyzed" : "Pending"}
                  </span>
                </div>

                <span className="document-id">
                  ID: {resume.id}
                </span>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
