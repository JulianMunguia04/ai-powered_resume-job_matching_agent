
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_URL;

    if (!backendUrl) {
      return NextResponse.json(
        { error: "BACKEND_URL is not configured." },
        { status: 500 }
      );
    }

    const baseUrl = backendUrl.replace(/\/+$/, "");

    // Request both totals from Flask.
    const [resumesResponse, jobsResponse] = await Promise.all([
      fetch(`${baseUrl}/api/resumes/`, { cache: "no-store" }),
      fetch(`${baseUrl}/api/jobs/`, { cache: "no-store" })
    ]);

    if (!resumesResponse.ok || !jobsResponse.ok) {
      throw new Error("Failed to retrieve dashboard statistics from Flask.");
    }

    const [resumesData, jobsData] = await Promise.all([
      resumesResponse.json(),
      jobsResponse.json()
    ]);

    return NextResponse.json({
      resumes: resumesData.total ?? 0,
      jobs: jobsData.total ?? 0
    });

  } catch (error) {
    console.error("Dashboard stats error:", error);

    return NextResponse.json(
      { error: "Unable to load dashboard statistics." },
      { status: 500 }
    );
  }
}
