"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import MatchCard from "@/components/MatchCard";

function getMatchScore(match) {
  const score = Number(match.scores?.hybrid);
  return Number.isFinite(score) ? score : -1;
}

function JobDetailPageContent() {
  const { id } = useParams();
  const router = useRouter();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [matches, setMatches] = useState([]);
  const [matchesLoading, setMatchesLoading] = useState(true);
  const [matchesError, setMatchesError] = useState("");

  useEffect(() => {
    if (!id) return;

    async function fetchJob() {
      try {
        const response = await fetch(`/api/jobs/${encodeURIComponent(id)}`, {
          cache: "no-store",
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Failed to load job.");
        }
        setJob(data.job);
      } catch (err) {
        console.error("Job detail error:", err);
        setError(err.message || "Unable to load job.");
      } finally {
        setLoading(false);
      }
    }

    async function fetchMatches() {
      try {
        const response = await fetch(
          `/api/matches/jobs/${encodeURIComponent(id)}?limit=5`,
          { cache: "no-store" }
        );
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Failed to load matching candidates.");
        }
        setMatches(data.matches || []);
      } catch (err) {
        console.error("Job matching error:", err);
        setMatchesError(err.message || "Unable to load matching candidates.");
      } finally {
        setMatchesLoading(false);
      }
    }

    fetchJob();
    fetchMatches();
  }, [id]);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="empty-state">
          <p>Loading job description...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="dashboard-container">
        <div className="empty-state">
          <h3>Unable to load job</h3>
          <p>{error || "Job not found."}</p>
          <button onClick={() => router.push("/jobs")}>
            Back to job descriptions
          </button>
        </div>
      </div>
    );
  }

  const skills = job.analysis?.skills || [];

  const sortedMatches = [...matches].sort(
    (a, b) => getMatchScore(b) - getMatchScore(a)
  );

  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">JOB PROFILE</p>
          <h1>{job.title}</h1>
          <p className="welcome-description">
            Individual job description and extracted requirements.
          </p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Position information</h2>
            <p>Stored job description and analysis details</p>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-caption">JOB TITLE</span>
          <h2>{job.title}</h2>
          <p>
            <strong>Job ID:</strong> {job.id}
          </p>
          <p>
            <strong>Embedding model:</strong>{" "}
            {job.embedding_model || "Unavailable"}
          </p>
          <p>
            <strong>Analysis status:</strong>{" "}
            {job.analysis ? "Analyzed" : "Pending"}
          </p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Extracted skills</h2>
            <p>{skills.length} skills identified in this job description</p>
          </div>
        </div>
        {skills.length > 0 ? (
          <div className="job-skills-list">
            {skills.map((skill, index) => {
              const name = typeof skill === "string" ? skill : skill.name;
              const requirementType =
                typeof skill === "object"
                  ? skill.requirement_type || "mentioned"
                  : "mentioned";
              return (
                <div className="job-skill-item" key={`${name}-${index}`}>
                  <span className="skill-tag">{name}</span>
                  <span className="skill-requirement">
                    {requirementType.replaceAll("_", " ")}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <p>No skills have been identified.</p>
        )}
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Job description</h2>
            <p>Complete extracted job description text</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="resume-raw-text">
            {job.description || "No job description available."}
          </div>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Matches</h2>
            <p>Top matching candidates for this position</p>
          </div>
          {!matchesLoading && !matchesError && (
            <span className="match-results-count">
              {sortedMatches.length} of 5 matches
            </span>
          )}
        </div>

        {matchesLoading ? (
          <div className="empty-state">
            <p>Finding the best matching candidates...</p>
          </div>
        ) : matchesError ? (
          <div className="empty-state">
            <h3>Unable to load matches</h3>
            <p>{matchesError}</p>
          </div>
        ) : sortedMatches.length > 0 ? (
          <div className="match-results-list">
            {sortedMatches.slice(0, 5).map((match) => (
              <MatchCard
                key={match.id || match.applicant?.id}
                match={match}
                type="job"
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h3>No matches found</h3>
            <p>
              No matching candidates are currently available for this position.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

export default function JobDetailPage() {
  return (
    <Suspense fallback={<div>Loading job...</div>}>
      <JobDetailPageContent />
    </Suspense>
  );
}
