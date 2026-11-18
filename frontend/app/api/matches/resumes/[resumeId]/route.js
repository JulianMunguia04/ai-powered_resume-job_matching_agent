
import { NextResponse } from "next/server";
import { backendUrl } from "@/lib/backend";

export async function GET(request, { params }) {
  try {
    const { resumeId } = await params;

    const { searchParams } = new URL(request.url);
    const limit = searchParams.get("limit") || "10";

    const response = await fetch(
      `${backendUrl}/api/matches/resumes/${encodeURIComponent(resumeId)}?limit=${encodeURIComponent(limit)}`,
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
    console.error("Resume matches API error:", error);

    return NextResponse.json(
      { error: error.message || "Unable to retrieve resume matches." },
      { status: 500 }
    );
  }
}
