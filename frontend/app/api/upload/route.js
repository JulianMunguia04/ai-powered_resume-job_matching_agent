
import { NextResponse } from "next/server";
import mammoth from "mammoth";
import { createRequire } from "node:module";
import path from "node:path";
import { checkRateLimit } from "@/lib/rateLimit";

const require = createRequire(
  path.join(process.cwd(), "package.json")
);

const pdfParse = require("pdf-parse");

export async function POST(request) {
  try {
    // Limit uploads to 5 requests per IP per minute.
    const rateLimit = await checkRateLimit(request, {
      limit: 5,
      windowMs: 60 * 1000,
      prefix: "upload",
    });

    if (rateLimit.unavailable) {
      return NextResponse.json(
        {
          error: "Upload service temporarily unavailable.",
          message: "The rate limiter could not connect to Redis.",
        },
        {
          status: 503,
          headers: {
            "Retry-After": String(rateLimit.retryAfter),
          },
        }
      );
    }

    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: "Too many uploads.",
          message: "You can upload up to 5 documents per minute. Please try again shortly.",
        },
        {
          status: 429,
          headers: {
            "Retry-After": String(rateLimit.retryAfter),
            "X-RateLimit-Limit": String(rateLimit.limit),
            "X-RateLimit-Remaining": "0",
          },
        }
      );
    }

    const formData = await request.formData();

    const type = formData.get("type");
    const file = formData.get("file");
    const title = formData.get("title");
    const candidateName = formData.get("candidateName");

    if (!["resume", "job"].includes(type)) {
      return NextResponse.json(
        { error: "Invalid document type." },
        { status: 400 }
      );
    }

    if (!file || typeof file.arrayBuffer !== "function") {
      return NextResponse.json(
        { error: "Please select a document." },
        { status: 400 }
      );
    }

    if (file.size > 10 * 1024 * 1024) {
      return NextResponse.json(
        { error: "File size cannot exceed 10 MB." },
        { status: 400 }
      );
    }

    const filename = file.name.toLowerCase();
    const buffer = Buffer.from(await file.arrayBuffer());

    let extractedText = "";

    if (filename.endsWith(".pdf")) {
      const result = await pdfParse(buffer);
      extractedText = result.text;
    } else if (filename.endsWith(".docx")) {
      const result = await mammoth.extractRawText({ buffer });
      extractedText = result.value;
    } else if (filename.endsWith(".txt")) {
      extractedText = buffer.toString("utf-8");
    } else {
      return NextResponse.json(
        { error: "Only PDF, DOCX, and TXT files are supported." },
        { status: 400 }
      );
    }

    extractedText = extractedText.trim();

    if (!extractedText) {
      return NextResponse.json(
        { error: "No readable text was found in this document." },
        { status: 400 }
      );
    }

    const backendUrl = process.env.BACKEND_URL;

    if (!backendUrl) {
      throw new Error("BACKEND_URL is not configured.");
    }

    let endpoint;
    let payload;

    if (type === "resume") {
      endpoint = "/api/resumes/";

      if (!candidateName || !candidateName.trim()) {
        return NextResponse.json(
          { error: "A candidate name is required." },
          { status: 400 }
        );
      }

      payload = {
        candidate_name: candidateName.trim(),
        text: extractedText,
      };
    } else {
      if (!title || !title.trim()) {
        return NextResponse.json(
          { error: "A job title is required." },
          { status: 400 }
        );
      }

      endpoint = "/api/jobs/";

      payload = {
        title: title.trim(),
        description: extractedText,
      };
    }

    const backendResponse = await fetch(
      `${backendUrl.replace(/\/$/, "")}${endpoint}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        cache: "no-store",
      }
    );

    const responseText = await backendResponse.text();

    let backendData;

    try {
      backendData = JSON.parse(responseText);
    } catch {
      backendData = { message: responseText };
    }

    if (!backendResponse.ok) {
      return NextResponse.json(
        {
          error:
            backendData.error ||
            backendData.message ||
            "The backend rejected the document.",
          backend: backendData,
        },
        {
          status: backendResponse.status,
          headers:
            backendResponse.status === 429
              ? {
                  "Retry-After":
                    backendResponse.headers.get("Retry-After") || "60",
                }
              : {},
        }
      );
    }

    return NextResponse.json(
      {
        success: true,
        type,
        filename: file.name,
        extractedCharacters: extractedText.length,
        document: backendData,
      },
      {
        headers: {
          "X-RateLimit-Limit": String(rateLimit.limit),
          "X-RateLimit-Remaining": String(rateLimit.remaining),
        },
      }
    );
  } catch (error) {
    console.error("Document upload error:", error);

    return NextResponse.json(
      {
        error: error.message || "An unexpected upload error occurred.",
      },
      { status: 500 }
    );
  }
}
