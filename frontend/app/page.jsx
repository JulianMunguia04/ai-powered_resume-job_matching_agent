
"use client";

import { useRef, useState } from "react";

function Icon({ name, size = 20 }) {
  const paths = {
    dashboard: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
    resume: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6M8 13h8M8 17h8" /></>,
    jobs: <><rect x="3" y="7" width="18" height="14" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2" /></>,
    matching: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4M8 11l2 2 4-4" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.6a8 8 0 0 1-1.7 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.7-1l-1.7.6-1.4-2.4 1.4-1.1a8 8 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.6a8 8 0 0 1 1.7-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.7 1l1.7-.6 1.4 2.4-1.4 1.1a8 8 0 0 1 0 2Z" /></>,
    upload: <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><path d="m17 8-5-5-5 5M12 3v12" /></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /></>,
    arrow: <><path d="M7 17 17 7M7 7h10v10" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    menu: <><path d="M4 6h16M4 12h16M4 18h16" /></>,
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}

export default function Home() {
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadType, setUploadType] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const resumeInput = useRef(null);
  const jobInput = useRef(null);

  function handleFileSelect(event, type) {
    const file = event.target.files?.[0];

    if (file) {
      setSelectedFile(file);
      setUploadType(type);
      setUploadOpen(false);
    }

    event.target.value = "";
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">T</div>
          <div>
            <h2>TalentMatch</h2>
            <span>Recruitment Intelligence</span>
          </div>
        </div>

        <div className="nav-section">
          <p className="nav-label">WORKSPACE</p>

          <a href="#" className="nav-item active">
            <Icon name="dashboard" />
            <span>Dashboard</span>
          </a>

          <a href="#documents" className="nav-item">
            <Icon name="resume" />
            <span>Resumes</span>
          </a>

          <a href="#documents" className="nav-item">
            <Icon name="jobs" />
            <span>Job Descriptions</span>
          </a>

          <a href="#matching" className="nav-item">
            <Icon name="matching" />
            <span>Matching</span>
          </a>
        </div>

        <div className="sidebar-bottom">
          <a href="#settings" className="nav-item">
            <Icon name="settings" />
            <span>Settings</span>
          </a>

          <div className="sidebar-profile">
            <div className="profile-avatar">TM</div>
            <div className="profile-info">
              <strong>Workspace</strong>
              <span>Recruitment Team</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle navigation"
          >
            <Icon name="menu" />
          </button>

          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Dashboard</strong>
          </div>

          <div className="topbar-actions">
            <div className="upload-wrapper">
              <button
                className="upload-button"
                onClick={() => setUploadOpen(!uploadOpen)}
              >
                <Icon name="upload" size={18} />
                Upload document
                <span className="dropdown-arrow">⌄</span>
              </button>

              {uploadOpen && (
                <div className="upload-dropdown">
                  <button onClick={() => resumeInput.current?.click()}>
                    <div className="dropdown-icon">
                      <Icon name="resume" />
                    </div>
                    <div>
                      <strong>Upload resume</strong>
                      <span>Add a candidate resume</span>
                    </div>
                  </button>

                  <button onClick={() => jobInput.current?.click()}>
                    <div className="dropdown-icon">
                      <Icon name="jobs" />
                    </div>
                    <div>
                      <strong>Upload job description</strong>
                      <span>Add a position to your workspace</span>
                    </div>
                  </button>
                </div>
              )}
            </div>

            <input
              ref={resumeInput}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              hidden
              onChange={(event) => handleFileSelect(event, "Resume")}
            />

            <input
              ref={jobInput}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              hidden
              onChange={(event) => handleFileSelect(event, "Job Description")}
            />
          </div>
        </header>

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

            <div className="date-indicator">
              <Icon name="clock" size={17} />
              Recruitment workspace
            </div>
          </section>

          {selectedFile && (
            <div className="selected-file">
              <div className="selected-file-icon">
                <Icon name="file" />
              </div>
              <div className="selected-file-info">
                <strong>{selectedFile.name}</strong>
                <span>
                  {uploadType} selected ·{" "}
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>
              <button
                className="remove-file"
                onClick={() => setSelectedFile(null)}
              >
                ×
              </button>
            </div>
          )}

          <section className="stats-grid" id="documents">
            <div className="stat-card">
              <div className="stat-top">
                <span className="stat-icon blue">
                  <Icon name="resume" size={21} />
                </span>
                <span className="stat-caption">DOCUMENTS</span>
              </div>
              <h2>0</h2>
              <p>Resumes uploaded</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span className="stat-icon purple">
                  <Icon name="jobs" size={21} />
                </span>
                <span className="stat-caption">POSITIONS</span>
              </div>
              <h2>0</h2>
              <p>Job descriptions</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span className="stat-icon green">
                  <Icon name="matching" size={21} />
                </span>
                <span className="stat-caption">ANALYSIS</span>
              </div>
              <h2>0</h2>
              <p>Matches generated</p>
            </div>
          </section>

          <section className="section-heading">
            <div>
              <h2>Get started</h2>
              <p>Choose an action to begin working with your documents.</p>
            </div>
          </section>

          <section className="action-grid">
            <button
              className="action-card"
              onClick={() => resumeInput.current?.click()}
            >
              <div className="action-icon blue">
                <Icon name="resume" size={23} />
              </div>
              <div className="action-content">
                <h3>Upload a resume</h3>
                <p>
                  Add candidate resumes for skill extraction and qualification
                  analysis.
                </p>
                <span className="action-link">
                  Select resume <Icon name="arrow" size={15} />
                </span>
              </div>
            </button>

            <button
              className="action-card"
              onClick={() => jobInput.current?.click()}
            >
              <div className="action-icon purple">
                <Icon name="jobs" size={23} />
              </div>
              <div className="action-content">
                <h3>Add a job description</h3>
                <p>
                  Analyze job requirements, responsibilities, and required
                  qualifications.
                </p>
                <span className="action-link">
                  Select job description <Icon name="arrow" size={15} />
                </span>
              </div>
            </button>

            <button
              className="action-card"
              onClick={() => {
                document.getElementById("matching")?.scrollIntoView({
                  behavior: "smooth",
                });
              }}
            >
              <div className="action-icon green">
                <Icon name="matching" size={23} />
              </div>
              <div className="action-content">
                <h3>Compare candidates</h3>
                <p>
                  Evaluate resume and job compatibility with semantic and
                  structured matching.
                </p>
                <span className="action-link">
                  Explore matching <Icon name="arrow" size={15} />
                </span>
              </div>
            </button>
          </section>

          <section className="activity-section" id="matching">
            <div className="activity-heading">
              <div>
                <h2>Recent activity</h2>
                <p>Keep track of your latest recruitment activity.</p>
              </div>
              <span className="activity-filter">All activity</span>
            </div>

            <div className="empty-state">
              <div className="empty-icon">
                <Icon name="file" size={27} />
              </div>
              <h3>No activity yet</h3>
              <p>
                Uploaded resumes, job descriptions, and matching results will
                appear here.
              </p>
              <button
                className="secondary-button"
                onClick={() => setUploadOpen(true)}
              >
                <Icon name="upload" size={16} />
                Upload your first document
              </button>
            </div>
          </section>

          <footer className="dashboard-footer">
            <span>TalentMatch</span>
            <span>AI-assisted recruitment screening</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
