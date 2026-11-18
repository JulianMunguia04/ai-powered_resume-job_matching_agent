
import Link from "next/link";

function StatusBadge({ status }) {
  const normalizedStatus = (status || "unknown")
    .toLowerCase()
    .replaceAll(" ", "_");

  const labels = {
    demonstrated: "Demonstrated",
    listed: "Listed",
    partial: "Partial",
    not_found: "Not found",
    below_minimum: "Below minimum",
  };

  return (
    <span className={`match-status match-status-${normalizedStatus}`}>
      {labels[normalizedStatus] || status || "Unknown"}
    </span>
  );
}

function MatchList({ title, items, emptyMessage }) {
  if (!items?.length) return null;

  return (
    <div className="match-detail-group">
      <h4>{title}</h4>
      <ul className="match-bullet-list">
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function MatchCard({
  match,
  type,
}) {
  const analysis = match.explanation?.analysis || {};
  const matching = match.matching || {};
  const score = Number(match.scores?.hybrid);

  const percentage = Number.isFinite(score)
    ? Math.round(score * 100)
    : null;

  const isResumeMatch = type === "resume";

  const profile = isResumeMatch
    ? match.job
    : match.applicant;

  const profileName = isResumeMatch
    ? profile?.title || "Untitled job"
    : profile?.candidate_name || "Candidate profile";

  const profileId = profile?.id;

  const profileUrl = profileId
    ? isResumeMatch
      ? `/jobs/${profileId}`
      : `/resumes/${profileId}`
    : null;

  const skillComparison =
    analysis.skill_comparison ||
    matching.requirements ||
    [];

  const requirementsSummary =
    matching.summary ||
    analysis.requirement_matching?.summary ||
    {};

  const educationRequirements =
    matching.education_requirements ||
    [];

  const experienceRequirements =
    matching.experience_requirements ||
    [];

  return (
    <article className="match-card">
      <div className="match-card-header">
        <div className="match-card-identity">
          <span className="match-card-label">
            {isResumeMatch ? "MATCHING JOB" : "MATCHING CANDIDATE"}
          </span>

          <h3>{profileName}</h3>

          {profileId && (
            <span className="match-card-id">
              {isResumeMatch ? "Job" : "Resume"} ID: {profileId}
            </span>
          )}
        </div>

        <div className="match-score">
          <span className="match-score-value">
            {percentage !== null ? `${percentage}%` : "N/A"}
          </span>
          <span className="match-score-caption">Match score</span>
        </div>
      </div>

      <div className="match-score-track">
        <div
          className="match-score-fill"
          style={{
            width: `${Math.min(100, Math.max(0, percentage ?? 0))}%`,
          }}
        />
      </div>

      <div className="match-card-body">
        {analysis.match_summary && (
          <div className="match-detail-group">
            <h4>Match summary</h4>
            <p>{analysis.match_summary}</p>
          </div>
        )}

        {analysis.overall_assessment && (
          <div className="match-detail-group">
            <h4>Overall assessment</h4>
            <p>{analysis.overall_assessment}</p>
          </div>
        )}

        <div className="match-two-column">
          <MatchList
            title="Strengths"
            items={analysis.strengths}
          />

          <MatchList
            title="Areas of concern"
            items={analysis.gaps}
          />
        </div>

        {skillComparison.length > 0 && (
          <div className="match-detail-group">
            <div className="match-section-heading">
              <h4>Skills and requirements</h4>
              <span className="match-requirement-count">
                {requirementsSummary.demonstrated ?? 0} demonstrated
                {" · "}
                {requirementsSummary.listed ?? 0} listed
                {" · "}
                {requirementsSummary.not_found ?? 0} not found
              </span>
            </div>

            <div className="match-skills-list">
              {skillComparison.map((item, index) => {
                const requirement =
                  typeof item === "string"
                    ? item
                    : item.requirement || item.name || "Requirement";

                const status =
                  typeof item === "string"
                    ? "unknown"
                    : item.status;

                return (
                  <div
                    className="match-skill-item"
                    key={`${requirement}-${index}`}
                  >
                    <div className="match-skill-main">
                      <strong>{requirement}</strong>

                      {item.explanation && (
                        <p>{item.explanation}</p>
                      )}

                      {item.evidence?.length > 0 && (
                        <div className="match-evidence">
                          <span>Resume evidence:</span>
                          {item.evidence.map((evidence, evidenceIndex) => (
                            <p key={evidenceIndex}>{evidence}</p>
                          ))}
                        </div>
                      )}

                      {item.transferable_evidence?.length > 0 && (
                        <div className="match-evidence">
                          <span>Transferable evidence:</span>
                          {item.transferable_evidence.map(
                            (evidence, evidenceIndex) => (
                              <p key={evidenceIndex}>{evidence}</p>
                            )
                          )}
                        </div>
                      )}
                    </div>

                    <StatusBadge status={status} />
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {(educationRequirements.length > 0 ||
          experienceRequirements.length > 0) && (
          <div className="match-two-column">
            {educationRequirements.length > 0 && (
              <div className="match-detail-group">
                <h4>Education requirements</h4>

                {educationRequirements.map((item, index) => (
                  <div className="match-requirement-item" key={index}>
                    <StatusBadge status={item.status} />
                    <p>
                      {item.requirement?.description ||
                        item.requirement?.field ||
                        "Education requirement"}
                    </p>
                    {item.explanation && <p>{item.explanation}</p>}
                  </div>
                ))}
              </div>
            )}

            {experienceRequirements.length > 0 && (
              <div className="match-detail-group">
                <h4>Experience requirements</h4>

                {experienceRequirements.map((item, index) => (
                  <div className="match-requirement-item" key={index}>
                    <StatusBadge status={item.status} />
                    <p>
                      {item.requirement?.evidence ||
                        "Experience requirement"}
                    </p>
                    {item.explanation && <p>{item.explanation}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {analysis.recommendation && (
          <div className="match-recommendation">
            <h4>Recommendation</h4>
            <p>{analysis.recommendation}</p>
          </div>
        )}
      </div>

      <div className="match-card-footer">
        {profileUrl ? (
          <Link href={profileUrl} className="match-profile-link">
            {isResumeMatch ? "View job description" : "View candidate profile"}
            <span aria-hidden="true">→</span>
          </Link>
        ) : (
          <span className="match-profile-unavailable">
            Profile unavailable
          </span>
        )}
      </div>
    </article>
  );
}
