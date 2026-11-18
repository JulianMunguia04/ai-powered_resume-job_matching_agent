
import { NextResponse } from "next/server";
import { backendUrl } from "@/lib/backend";

export async function GET() {
  try {
    // Retrieve resumes, jobs, and saved matches in parallel.
    const [resumesResponse, jobsResponse, matchesResponse] =
      await Promise.all([
        fetch(`${backendUrl}/api/resumes/`, { cache: "no-store" }),
        fetch(`${backendUrl}/api/jobs/`, { cache: "no-store" }),
        fetch(`${backendUrl}/api/matches/`, { cache: "no-store" }),
      ]);

    if (
      !resumesResponse.ok ||
      !jobsResponse.ok ||
      !matchesResponse.ok
    ) {
      throw new Error("Failed to retrieve dashboard statistics.");
    }

    const [resumesData, jobsData, matchesData] = await Promise.all([
      resumesResponse.json(),
      jobsResponse.json(),
      matchesResponse.json(),
    ]);

    return NextResponse.json({
      resumes: resumesData.total ?? resumesData.resumes?.length ?? 0,
      jobs: jobsData.total ?? jobsData.jobs?.length ?? 0,
      matches: matchesData.total ?? matchesData.matches?.length ?? 0,
    });
  } catch (error) {
    console.error("Dashboard stats error:", error);

    return NextResponse.json(
      { error: "Unable to load dashboard statistics." },
      { status: 500 }
    );
  }
}
