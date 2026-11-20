
"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import {
  getRecentActivity,
  ACTIVITY_EVENT,
} from "@/lib/recentActivity";

export default function Dashboard() {
  const [resumeCount, setResumeCount] = useState(null);
  const [jobCount, setJobCount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);
  const [matchCount, setMatchCount] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch("/api/stats", {
        cache: "no-store",
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

  const refreshRecentActivity = useCallback(() => {
    setRecentActivity(getRecentActivity());
  }, []);

  useEffect(() => {
    fetchStats();
    refreshRecentActivity();

    window.addEventListener("workspace-data-updated", fetchStats);
    window.addEventListener(ACTIVITY_EVENT, refreshRecentActivity);

    return () => {
      window.removeEventListener("workspace-data-updated", fetchStats);
      window.removeEventListener(ACTIVITY_EVENT, refreshRecentActivity);
    };
  }, [fetchStats, refreshRecentActivity]);

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
          <h2>
            {loading ? "..." : statsError ? "—" : matchCount ?? 0}
          </h2>
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
        <div className="recent-activity-header">
          <div>
            <h2>Recent activity</h2>
            <p>Your latest uploaded resumes and job descriptions.</p>
          </div>
        </div>

        {recentActivity.length === 0 ? (
          <div className="empty-state">
            <h3>No recent activity</h3>
            <p>
              Newly uploaded resumes and job descriptions will
              appear here for five minutes.
            </p>
          </div>
        ) : (
          <div className="recent-activity-grid">
            {recentActivity.map((activity) => {
              const isResume = activity.type === "resume";

              return (
                <Link
                  key={`${activity.type}-${activity.id}`}
                  href={`/${isResume ? "resumes" : "jobs"}/${encodeURIComponent(activity.id)}`}
                  className="recent-activity-card"
                >
                  <div
                    className={`recent-activity-icon ${
                      isResume ? "resume" : "job"
                    }`}
                  >
                    {isResume ? "▤" : "▣"}
                  </div>

                  <div className="recent-activity-content">
                    <span className="recent-activity-type">
                      {isResume ? "RESUME UPLOADED" : "JOB ADDED"}
                    </span>

                    <h3>{activity.title}</h3>

                    <p>
                      {new Date(activity.createdAt).toLocaleTimeString(
                        undefined,
                        {
                          hour: "numeric",
                          minute: "2-digit",
                        }
                      )}
                      {" · "}Expires after 5 minutes
                    </p>
                  </div>

                  <span className="recent-activity-arrow">→</span>
                </Link>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
