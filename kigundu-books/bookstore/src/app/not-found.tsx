import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-5 py-24">
      <h1 className="text-3xl font-semibold">Page not found</h1>
      <p className="mt-3 text-ink-muted">The page may have moved, or the book is not published yet.</p>
      <Link href="/" className="mt-6 inline-block rounded bg-navy-900 px-5 py-3 text-paper hover:bg-navy-800">Back to home</Link>
    </div>
  );
}
