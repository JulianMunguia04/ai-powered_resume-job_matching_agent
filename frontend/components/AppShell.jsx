
"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { label: "Dashboard", href: "/", icon: "▦" },
  { label: "Resumes", href: "/resumes", icon: "▤" },
  { label: "Job Descriptions", href: "/jobs", icon: "▣" },
  { label: "Matching", href: "/matching", icon: "⌕" },
];

export default function AppShell({ children }) {
  const pathname = usePathname();

  const [uploadType, setUploadType] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragging, setDragging] = useState(false);

  const [uploadTitle, setUploadTitle] = useState("");
  const [candidateName, setCandidateName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadNotice, setUploadNotice] = useState("");

  const fileInput = useRef(null);

  function openUpload(type) {
    setUploadType(type);
    setSelectedFile(null);
    setUploadTitle("");
    setCandidateName("");
    setUploadError("");
    setDragging(false);
  }

  function closeUpload() {
    if (isUploading) return;

    setUploadType(null);
    setSelectedFile(null);
    setUploadTitle("");
    setCandidateName("");
    setUploadError("");
    setDragging(false);
  }

  function switchUploadType(type) {
    setUploadType(type);
    setSelectedFile(null);
    setUploadTitle("");
    setCandidateName("");
    setUploadError("");
    setDragging(false);
  }

  async function submitUpload() {
    if (!selectedFile || isUploading) return;

    if (uploadType === "Job Description" && !uploadTitle.trim()) {
      setUploadError("Please enter a job title.");
      return;
    }

    if (uploadType === "Resume" && !candidateName.trim()) {
      setUploadError("Please enter the candidate's name.");
      return;
    }

    setIsUploading(true);
    setUploadError("");

    try {
      const formData = new FormData();

      formData.append(
        "type",
        uploadType === "Resume" ? "resume" : "job"
      );

      formData.append("file", selectedFile);

      if (uploadType === "Job Description") {
        formData.append("title", uploadTitle.trim());
      }

      if (uploadType === "Resume") {
        formData.append("candidateName", candidateName.trim());
      }

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const responseText = await response.text();

      console.log("Upload status:", response.status);
      console.log("Upload response:", responseText);

      let data;

      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(
          `Invalid server response (${response.status}): ${responseText.slice(0, 300)}`
        );
      }

      if (!response.ok) {
        throw new Error(data.error || "Upload failed.");
      }

      window.dispatchEvent(new Event("workspace-data-updated"));

      setUploadNotice(
        `${data.filename} was successfully uploaded and analyzed.`
      );

      setUploadType(null);
      setSelectedFile(null);
      setUploadTitle("");
      setCandidateName("");
      setUploadError("");

    } catch (error) {
      console.error("Upload error:", error);
      setUploadError(error.message);
    } finally {
      setIsUploading(false);
    }
  }

  function handleFile(file) {
    if (!file) return;

    const allowedExtensions = [".pdf", ".docx", ".txt"];

    const valid = allowedExtensions.some((extension) =>
      file.name.toLowerCase().endsWith(extension)
    );

    if (!valid) {
      alert("Please select a PDF, DOCX, or TXT file.");
      return;
    }

    setSelectedFile(file);
    setUploadError("");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <img
            src="/logo-square.png"
            alt="MatchPilot.ai Logo"
            className="brand-icon"
          />
          <div>
            <h2>MatchPilot.ai</h2>
            <span>Recruitment Intelligence</span>
          </div>
        </Link>

        <div className="nav-section">
          <p className="nav-label">WORKSPACE</p>

          {navigation.map((item) => {
            const active = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-item ${active ? "active" : ""}`}
              >
                <span className="nav-symbol">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

        <div className="sidebar-bottom">
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
          <div className="breadcrumb">
            Workspace <span>/</span>
            <strong>
              {navigation.find((item) => item.href === pathname)?.label ||
                "Dashboard"}
            </strong>
          </div>

          <div className="topbar-logo-container">
            <img
              src="/logo.png"
              alt="MatchPilot.ai"
              className="topbar-logo"
            />
          </div>

          <div className="upload-wrapper">
            <button
              className="upload-button"
              onClick={() => openUpload("Resume")}
            >
              <span>＋</span> Upload document
            </button>

            <div className="upload-quick-menu">
              <button onClick={() => openUpload("Resume")}>
                Upload resume
              </button>
              <button onClick={() => openUpload("Job Description")}>
                Upload job description
              </button>
            </div>
          </div>
        </header>

        {uploadNotice && (
          <div className="upload-success">
            <span>✓</span>
            {uploadNotice}
            <button onClick={() => setUploadNotice("")}>×</button>
          </div>
        )}

        <div className="page-content">{children}</div>
      </main>

      {uploadType && (
        <div className="upload-overlay" onClick={closeUpload}>
          <section
            className="upload-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">DOCUMENT UPLOAD</span>
                <h2>Upload {uploadType.toLowerCase()}</h2>
                <p>
                  Add a document to your recruitment workspace for analysis.
                </p>
              </div>

              <button
                className="modal-close"
                onClick={closeUpload}
                aria-label="Close upload"
              >
                ×
              </button>
            </div>

            <div className="upload-type-selector">
              <button
                className={uploadType === "Resume" ? "selected" : ""}
                onClick={() => switchUploadType("Resume")}
              >
                Resume
              </button>

              <button
                className={
                  uploadType === "Job Description" ? "selected" : ""
                }
                onClick={() => switchUploadType("Job Description")}
              >
                Job description
              </button>
            </div>

            {uploadType === "Resume" && (
              <div className="job-title-field">
                <label htmlFor="candidate-name">Candidate name</label>
                <input
                  id="candidate-name"
                  type="text"
                  placeholder="e.g. Jane Smith"
                  value={candidateName}
                  onChange={(event) => setCandidateName(event.target.value)}
                />
              </div>
            )}

            {uploadType === "Job Description" && (
              <div className="job-title-field">
                <label htmlFor="job-title">Job title</label>
                <input
                  id="job-title"
                  type="text"
                  placeholder="e.g. Junior Software Developer"
                  value={uploadTitle}
                  onChange={(event) => setUploadTitle(event.target.value)}
                />
              </div>
            )}

            <input
              ref={fileInput}
              type="file"
              accept=".pdf,.docx,.txt"
              hidden
              onChange={(event) => handleFile(event.target.files?.[0])}
            />

            <div
              className={`drop-zone ${dragging ? "dragging" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(event) => {
                event.preventDefault();
                setDragging(false);
                handleFile(event.dataTransfer.files?.[0]);
              }}
            >
              <div className="drop-icon">↑</div>

              {selectedFile ? (
                <>
                  <h3>{selectedFile.name}</h3>
                  <p>
                    {(selectedFile.size / 1024).toFixed(1)} KB · Ready to
                    upload
                  </p>
                  <button
                    className="remove-upload"
                    onClick={() => setSelectedFile(null)}
                  >
                    Remove file
                  </button>
                </>
              ) : (
                <>
                  <h3>Drag and drop your file here</h3>
                  <p>Or browse files from your computer</p>
                  <button
                    className="browse-button"
                    onClick={() => fileInput.current?.click()}
                  >
                    Browse files
                  </button>
                </>
              )}
            </div>

            <div className="upload-requirements">
              <span>Supported formats: PDF, DOCX, TXT</span>
              <span>Maximum file size: 10 MB</span>
            </div>

            {uploadError && (
              <div className="upload-error">
                {uploadError}
              </div>
            )}

            <div className="modal-actions">
              <button
                className="cancel-button"
                onClick={closeUpload}
                disabled={isUploading}
              >
                Cancel
              </button>

              <button
                className="confirm-upload"
                disabled={
                  !selectedFile ||
                  isUploading ||
                  (uploadType === "Job Description" && !uploadTitle.trim()) ||
                  (uploadType === "Resume" && !candidateName.trim())
                }
                onClick={submitUpload}
              >
                {isUploading ? "Processing document..." : "Upload document"}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
