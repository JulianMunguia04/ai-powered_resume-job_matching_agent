
import { NextResponse } from "next/server";
import mammoth from "mammoth";
import pdf from "pdf-parse";

export const runtime = "nodejs";

export async function POST(request) {
  try {
    const formData = await request.formData();

    const type = formData.get("type");
    const file = formData.get("file");
    const title = formData.get("title");

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
      const result = await pdf(buffer);
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
      payload = {
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
        { status: backendResponse.status }
      );
    }

    return NextResponse.json({
      success: true,
      type,
      filename: file.name,
      extractedCharacters: extractedText.length,
      document: backendData,
    });
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
