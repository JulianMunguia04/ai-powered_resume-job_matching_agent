
"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

function ResumeDetailPageContent() {
  const { id } = useParams();
  const router = useRouter();

  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    async function fetchResume() {
      try {
        const response = await fetch(
          `/api/resumes/${encodeURIComponent(id)}`,
          { cache: "no-store" }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to load resume.");
        }

        setResume(data.resume);
      } catch (err) {
        console.error("Resume detail error:", err);
        setError(err.message || "Unable to load resume.");
      } finally {
        setLoading(false);
      }
    }

    fetchResume();
  }, [id]);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="empty-state">
          <p>Loading candidate profile...</p>
        </div>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="dashboard-container">
        <div className="empty-state">
          <h3>Unable to load candidate</h3>
          <p>{error || "Resume not found."}</p>
          <button onClick={() => router.push("/resumes")}>
            Back to resumes
          </button>
        </div>
      </div>
    );
  }

  const skills = resume.analysis?.skills || [];

  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">CANDIDATE PROFILE</p>
          <h1>{resume.candidate_name || "Candidate Resume"}</h1>
          <p className="welcome-description">
            Individual candidate information and resume analysis.
          </p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Candidate information</h2>
            <p>Stored resume and analysis details</p>
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-caption">CANDIDATE NAME</span>
          <h2>{resume.candidate_name || "Unknown candidate"}</h2>
          <p>
            <strong>Resume ID:</strong> {resume.id}
          </p>
          <p>
            <strong>Embedding model:</strong>{" "}
            {resume.embedding_model || "Unavailable"}
          </p>
          <p>
            <strong>Analysis status:</strong>{" "}
            {resume.analysis ? "Analyzed" : "Pending"}
          </p>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Extracted skills</h2>
            <p>{skills.length} skills identified in this resume</p>
          </div>
        </div>

        <div className="document-skills">
          {skills.length > 0 ? (
            skills.map((skill, index) => {
              const name =
                typeof skill === "string" ? skill : skill.name;

              return (
                <span
                  className="skill-tag"
                  key={`${name}-${index}`}
                >
                  {name}
                </span>
              );
            })
          ) : (
            <p>No skills have been identified.</p>
          )}
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Resume</h2>
            <p>Complete extracted resume text</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="resume-raw-text">
            {resume.text || "No resume text available."}
          </div>
        </div>
      </section>

      <section className="activity-section">
        <div className="activity-heading">
          <div>
            <h2>Matches</h2>
            <p>Job opportunities matched to this candidate</p>
          </div>
        </div>

        <div className="empty-state">
          <h3>No matches yet</h3>
          <p>
            Candidate-to-job matching results will appear here once
            this feature is implemented.
          </p>
        </div>
      </section>
    </div>
  );
}

export default function ResumeDetailPage() {
  return (
    <Suspense fallback={<div>Loading resume...</div>}>
      <ResumeDetailPageContent />
    </Suspense>
  );
}