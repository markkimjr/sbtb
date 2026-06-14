import Link from "next/link";

export default function AuthLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <div className="px-8 py-6">
        <Link
          href="/fighters"
          className="ink-stamp font-display italic text-xl px-2"
        >
          saved by the bell
        </Link>
      </div>
      <main className="flex-1 grid place-items-center px-6 pb-16">
        <div className="w-full max-w-sm">{children}</div>
      </main>
    </div>
  );
}
