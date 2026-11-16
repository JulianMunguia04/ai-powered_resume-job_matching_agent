
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

  const fileInput = useRef(null);

  function openUpload(type) {
    setUploadType(type);
    setSelectedFile(null);
  }

  function closeUpload() {
    setUploadType(null);
    setSelectedFile(null);
  }

  function handleFile(file) {
    if (!file) return;

    const allowedExtensions = [".pdf", ".doc", ".docx", ".txt"];
    const valid = allowedExtensions.some((extension) =>
      file.name.toLowerCase().endsWith(extension)
    );

    if (!valid) {
      alert("Please select a PDF, DOC, DOCX, or TXT file.");
      return;
    }

    setSelectedFile(file);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <div className="brand-icon">T</div>
          <div>
            <h2>TalentMatch</h2>
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
                onClick={() => {
                  setUploadType("Resume");
                  setSelectedFile(null);
                }}
              >
                Resume
              </button>

              <button
                className={
                  uploadType === "Job Description" ? "selected" : ""
                }
                onClick={() => {
                  setUploadType("Job Description");
                  setSelectedFile(null);
                }}
              >
                Job description
              </button>
            </div>

            <input
              ref={fileInput}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
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
              <span>Supported formats: PDF, DOC, DOCX, TXT</span>
              <span>Maximum file size: 10 MB</span>
            </div>

            <div className="modal-actions">
              <button className="cancel-button" onClick={closeUpload}>
                Cancel
              </button>
              <button
                className="confirm-upload"
                disabled={!selectedFile}
                onClick={() => {
                  alert(
                    "The upload interface is ready. We will connect this to the Flask API next."
                  );
                }}
              >
                Continue
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
