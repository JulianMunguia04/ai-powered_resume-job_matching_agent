
import { NextResponse } from "next/server";
import { backendUrl } from "@/lib/backend";

export async function GET(request, { params }) {
  try {
    const { jobId } = await params;

    const { searchParams } = new URL(request.url);
    const limit = searchParams.get("limit") || "10";

    const response = await fetch(
      `${backendUrl}/api/matches/jobs/${encodeURIComponent(jobId)}?limit=${encodeURIComponent(limit)}`,
      {
        cache: "no-store",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, {
        status: response.status,
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Job matches API error:", error);

    return NextResponse.json(
      { error: error.message || "Unable to retrieve job matches." },
      { status: 500 }
    );
  }
}
