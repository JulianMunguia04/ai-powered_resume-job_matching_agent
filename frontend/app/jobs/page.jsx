"use client";

import Link from "next/link";

import { useCallback, useEffect, useState } from "react";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchJobs = useCallback(async () => {
    try {
      const response = await fetch("/api/jobs", {
        cache: "no-store",
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

  const analyzedCount = jobs.filter((job) => job.is_analyzed).length;
  const pendingCount = total - analyzedCount;

  function formatDate(date) {
    if (!date) return "Date unavailable";

    return new Date(date).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
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
            {jobs.map((job) => {
              const skills = job.analysis?.skills || [];
              const visibleSkills = skills.slice(0, 3);
              const remainingSkills = Math.max(0, skills.length - 3);

              return (
                <Link
                  href={`/jobs/${job.id}`}
                  className="document-card document-card-link"
                  key={job.id}
                >
                  <div className="document-card-header">
                    <div className="document-card-title">
                      <h3>{job.title}</h3>
                      <p>Added {formatDate(job.created_at)}</p>
                    </div>

                    <span
                      className={`document-status ${
                        job.is_analyzed ? "success" : "pending"
                      }`}
                    >
                      {job.is_analyzed ? "Analyzed" : "Pending"}
                    </span>
                  </div>

                  <p className="document-description">{job.description}</p>

                  <div className="document-skills">
                    {visibleSkills.map((skill, index) => {
                      const skillName =
                        typeof skill === "object" && skill !== null
                          ? skill.name
                          : skill;

                      return (
                        <span
                          className="skill-tag"
                          key={`${skillName}-${index}`}
                          title={
                            typeof skill === "object" ? skill.evidence : undefined
                          }
                        >
                          {skillName}
                        </span>
                      );
                    })}

                    {remainingSkills > 0 && (
                      <span className="skill-tag skill-more">
                        +{remainingSkills}
                      </span>
                    )}

                    {skills.length === 0 && (
                      <span className="no-skills">No skills detected</span>
                    )}
                  </div>

                  <span className="document-id">ID: {job.id}</span>
                </Link>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
