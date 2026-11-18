
"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

export default function Dashboard() {
  const [resumeCount, setResumeCount] = useState(null);
  const [jobCount, setJobCount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);
  const [matchCount, setMatchCount] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch("/api/stats", {
        cache: "no-store"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to load statistics.");
      }

      setResumeCount(data.resumes);
      setJobCount(data.jobs);
      setStatsError(false);
      setMatchCount(data.matches);

    } catch (error) {
      console.error("Dashboard statistics error:", error);
      setStatsError(true);

    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Load counts when the dashboard opens.
    fetchStats();

    // Refresh counts after a successful document upload.
    window.addEventListener("workspace-data-updated", fetchStats);

    return () => {
      window.removeEventListener("workspace-data-updated", fetchStats);
    };
  }, [fetchStats]);

  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h1>Recruitment Dashboard</h1>
          <p className="welcome-description">
            Manage candidates, analyze job requirements, and discover
            meaningful matches.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        <Link href="/resumes" className="stat-card">
          <span className="stat-caption">CANDIDATES</span>
          <h2>
            {loading ? "..." : statsError ? "—" : resumeCount}
          </h2>
          <p>Resumes uploaded</p>
        </Link>

        <Link href="/jobs" className="stat-card">
          <span className="stat-caption">POSITIONS</span>
          <h2>
            {loading ? "..." : statsError ? "—" : jobCount}
          </h2>
          <p>Job descriptions</p>
        </Link>

        <Link href="/matching" className="stat-card">
          <span className="stat-caption">ANALYSIS</span>
          <h2>{loading ? "..." : statsError ? "—" : matchCount ?? 0}</h2>
          <p>Matches generated</p>
        </Link>
      </section>

      {statsError && (
        <p role="alert">
          Unable to load dashboard statistics. Please refresh the page.
        </p>
      )}

      <section className="section-heading">
        <div>
          <h2>Get started</h2>
          <p>Choose an area of your recruitment workspace.</p>
        </div>
      </section>

      <section className="action-grid">
        <Link href="/resumes" className="action-card">
          <div className="action-icon blue">▤</div>
          <h3>Manage resumes</h3>
          <p>Upload and analyze candidate qualifications and experience.</p>
          <span className="action-link">View resumes →</span>
        </Link>

        <Link href="/jobs" className="action-card">
          <div className="action-icon purple">▣</div>
          <h3>Manage job descriptions</h3>
          <p>Review job requirements, skills, and responsibilities.</p>
          <span className="action-link">View jobs →</span>
        </Link>

        <Link href="/matching" className="action-card">
          <div className="action-icon green">⌕</div>
          <h3>Compare candidates</h3>
          <p>Evaluate compatibility using semantic and structured matching.</p>
          <span className="action-link">Explore matching →</span>
        </Link>
      </section>

      <section className="activity-section">
        <h2>Recent activity</h2>
        <div className="empty-state">
          <h3>No activity yet</h3>
          <p>Your uploaded documents and matching results will appear here.</p>
        </div>
      </section>
    </div>
  );
}
