
import { NextResponse } from "next/server";
import { backendUrl } from "@/lib/backend";

export async function GET() {
  try {
    const response = await fetch(`${backendUrl}/api/matches/`, {
      cache: "no-store",
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, {
        status: response.status,
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Matches API error:", error);

    return NextResponse.json(
      { error: error.message || "Unable to retrieve matches." },
      { status: 500 }
    );
  }
}
