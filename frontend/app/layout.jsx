
import "./globals.css";
import AppShell from "../components/AppShell";

export const metadata = {
  title: "MatchPilot.ai | Recruitment Intelligence",
  description: "AI-powered recruitment screening and resume matching.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
