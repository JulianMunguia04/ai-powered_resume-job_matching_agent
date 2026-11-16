import "./globals.css";

export const metadata = {
  title: "TalentMatch | Recruitment Intelligence",
  description:
    "AI-powered recruitment screening and resume matching platform.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}