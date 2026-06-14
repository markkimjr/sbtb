import type { Metadata } from "next";
import { Toaster } from "sonner";
import { fraunces, inter } from "@/lib/fonts";
import { AuthListener } from "@/providers/auth-listener";
import { QueryProvider } from "@/providers/query-provider";
import { ThemeProvider } from "@/providers/theme-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "saved by the bell",
  description:
    "Boxing reminders, hand-drawn. We ring the bell when your fighters fight next.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${inter.variable}`}
      suppressHydrationWarning
    >
      <body>
        <ThemeProvider>
          <QueryProvider>
            <AuthListener />
            {children}
            <Toaster
              position="bottom-right"
              toastOptions={{
                style: {
                  background: "var(--color-parchment)",
                  color: "var(--color-ink)",
                  border: "1px solid var(--color-sand)",
                  borderLeft: "4px solid var(--color-persimmon)",
                },
              }}
            />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
