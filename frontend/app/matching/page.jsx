
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

function getCollection(data, key) {
  if (Array.isArray(data)) return data;

  return (
    data?.[key] ||
    data?.items ||
    data?.data ||
    []
  );
}

function formatScore(scores) {
  const score = Number(scores?.hybrid);

  if (!Number.isFinite(score)) return "—";

  return `${Math.round(score * 100)}%`;
}

function formatDate(value) {
  if (!value) return "Recently";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "Recently";

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function MatchingPage() {
  const [matches, setMatches] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function fetchDashboardData() {
      try {
        setLoading(true);
        setError("");

        const endpoints = [
          "/api/matches/",
          "/api/resumes/",
          "/api/jobs/",
        ];

        const responses = await Promise.all(
          endpoints.map((endpoint) =>
            fetch(endpoint, {
              cache: "no-store",
              signal: controller.signal,
            })
          )
        );

        const data = await Promise.all(
          responses.map(async (response) => {
            const result = await response.json();

            if (!response.ok) {
              throw new Error(
                result.error || "Unable to load dashboard data."
              );
            }

            return result;
          })
        );

        setMatches(getCollection(data[0], "matches"));
        setResumes(getCollection(data[1], "resumes"));
        setJobs(getCollection(data[2], "jobs"));
      } catch (err) {
        if (err.name === "AbortError") return;

        console.error("Matching dashboard error:", err);
        setError(err.message || "Unable to load matching dashboard.");
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchDashboardData();

    return () => controller.abort();
  }, []);

  // Create lookup maps for profile names and job titles.
  const resumeMap = new Map(
    resumes.map((resume) => [String(resume.id), resume])
  );

  const jobMap = new Map(
    jobs.map((job) => [String(job.id), job])
  );

  // Show the most recently saved comparisons first.
  const recentMatches = [...matches]
    .sort(
      (a, b) =>
        new Date(b.created_at || 0) -
        new Date(a.created_at || 0)
    )
    .slice(0, 8);

  return (
    <div className="dashboard-container matching-dashboard">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">INTELLIGENT SCREENING</p>

          <h1>Candidate Matching</h1>

          <p className="welcome-description">
            Compare candidate resumes against job requirements and
            understand how closely they align.
          </p>
        </div>
      </section>

      {/* Dashboard statistics */}
      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-caption">MATCHES</span>

          <h2>
            {loading ? "—" : matches.length}
          </h2>

          <p>Total comparisons</p>
        </div>

        <div className="stat-card">
          <span className="stat-caption">CANDIDATES</span>

          <h2>
            {loading ? "—" : resumes.length}
          </h2>

          <p>Available resumes</p>
        </div>

        <div className="stat-card">
          <span className="stat-caption">POSITIONS</span>

          <h2>
            {loading ? "—" : jobs.length}
          </h2>

          <p>Available jobs</p>
        </div>
      </section>

      {/* Recent matching activity */}
      <section className="activity-section">
        <div className="matching-section-header">
          <div>
            <h2>Recent matches</h2>
            <p className="welcome-description">
              Your latest saved resume-job comparisons.
            </p>
          </div>

          <span className="match-results-count">
            {loading ? "Loading..." : `${matches.length} total`}
          </span>
        </div>

        {loading && (
          <div className="empty-state">
            <h3>Loading matching data...</h3>
            <p>
              Retrieving your candidates, positions, and saved matches.
            </p>
          </div>
        )}

        {!loading && error && (
          <div className="empty-state">
            <h3>Unable to load matching data</h3>
            <p>{error}</p>

            <button
              type="button"
              className="matching-retry-button"
              onClick={() => window.location.reload()}
            >
              Try again
            </button>
          </div>
        )}

        {!loading && !error && matches.length === 0 && (
          <div className="empty-state">
            <h3>Ready to find a match?</h3>

            <p>
              Once resumes and job descriptions are uploaded, you
              can compare candidates using semantic scoring and
              structured requirement analysis.
            </p>

            {resumes.length === 0 && jobs.length === 0 && (
              <p>
                Start by uploading resumes and adding job descriptions.
              </p>
            )}
          </div>
        )}

        {!loading && !error && matches.length > 0 && (
          <div className="recent-matches-list">
            {recentMatches.map((match) => {
              const resume = resumeMap.get(
                String(match.resume_id)
              );

              const job = jobMap.get(
                String(match.job_id)
              );

              const candidateName =
                resume?.candidate_name || "Candidate profile";

              const jobTitle =
                job?.title || "Job position";

              const summary =
                match.analysis?.match_summary ||
                match.analysis?.overall_assessment ||
                match.text ||
                "No match summary available.";

              return (
                <article
                  className="recent-match-card"
                  key={match.id}
                >
                  <div className="recent-match-main">
                    <div className="recent-match-identities">
                      <div>
                        <span className="recent-match-label">
                          CANDIDATE
                        </span>

                        {match.resume_id ? (
                          <Link
                            href={`/resumes/${match.resume_id}`}
                            className="recent-match-name"
                          >
                            {candidateName}
                          </Link>
                        ) : (
                          <span className="recent-match-name">
                            {candidateName}
                          </span>
                        )}
                      </div>

                      <span className="recent-match-separator">
                        →
                      </span>

                      <div>
                        <span className="recent-match-label">
                          POSITION
                        </span>

                        {match.job_id ? (
                          <Link
                            href={`/jobs/${match.job_id}`}
                            className="recent-match-name"
                          >
                            {jobTitle}
                          </Link>
                        ) : (
                          <span className="recent-match-name">
                            {jobTitle}
                          </span>
                        )}
                      </div>
                    </div>

                    <p className="recent-match-summary">
                      {summary}
                    </p>

                    <span className="recent-match-date">
                      Compared {formatDate(match.created_at)}
                    </span>
                  </div>

                  <div className="recent-match-score">
                    <span className="recent-match-label">
                      MATCH SCORE
                    </span>

                    <strong>
                      {formatScore(match.scores)}
                    </strong>

                    <Link
                      href={
                        match.resume_id
                          ? `/resumes/${match.resume_id}`
                          : match.job_id
                            ? `/jobs/${match.job_id}`
                            : "/matches"
                      }
                      className="recent-match-link"
                    >
                      View details →
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
