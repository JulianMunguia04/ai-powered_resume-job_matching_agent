
import { NextResponse } from "next/server";
import { loadEnvConfig } from "@next/env";
import path from "node:path";

loadEnvConfig(path.resolve(process.cwd(), ".."));

export async function GET(request, { params }) {
  try {
    const { id } = await params;
    const backendUrl = process.env.BACKEND_URL;

    if (!backendUrl) {
      throw new Error("BACKEND_URL is not configured.");
    }

    const response = await fetch(
      `${backendUrl.replace(/\/+$/, "")}/api/resumes/${encodeURIComponent(id)}`,
      { cache: "no-store" }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, {
        status: response.status,
      });
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error("Individual resume API error:", error);

    return NextResponse.json(
      { error: error.message || "Unable to retrieve resume." },
      { status: 500 }
    );
  }
}
