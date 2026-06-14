import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="min-h-screen grid place-items-center px-6">
      <div className="max-w-md text-center space-y-4">
        <h1 className="font-display italic text-4xl">Out of the ring.</h1>
        <p className="text-sm opacity-75">
          We couldn&apos;t find the page you were looking for.
        </p>
        <Link href="/fighters">
          <Button>Back to fighters</Button>
        </Link>
      </div>
    </div>
  );
}
