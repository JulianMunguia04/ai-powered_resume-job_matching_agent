
import { NextResponse } from "next/server";
import { loadEnvConfig } from "@next/env";
import path from "node:path";

loadEnvConfig(path.resolve(process.cwd(), ".."));

export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_URL;

    if (!backendUrl) {
      throw new Error("BACKEND_URL is not configured.");
    }

    const response = await fetch(
      `${backendUrl.replace(/\/+$/, "")}/api/jobs/`,
      { cache: "no-store" }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to retrieve jobs.");
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error("Jobs API error:", error);

    return NextResponse.json(
      { error: error.message || "Unable to retrieve jobs." },
      { status: 500 }
    );
  }
}
