import type { Metadata } from "next";
import { filterOptions, listPublishedBooks } from "@/lib/books";
import { BookCard } from "@/components/BookCard";

export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "Mathematics textbooks",
  description: "Browse mathematics, statistics and numerical methods textbooks for Uganda.",
  alternates: { canonical: "/books" },
};

type SP = { q?: string; subject?: string; level?: string; format?: string };
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v)?.slice(0, 100) || undefined;

export default async function Books({ searchParams }: { searchParams: Record<string, string | string[] | undefined> }) {
  const q = one(searchParams.q), subject = one(searchParams.subject), level = one(searchParams.level);
  const fmt = one(searchParams.format);
  const format = fmt === "PHYSICAL" || fmt === "DIGITAL" ? fmt : undefined;
  const [books, opts] = await Promise.all([
    listPublishedBooks({ q, subject, level, format }),
    filterOptions(),
  ]);
  const filtered = !!(q || subject || level || format);
  const field = "mt-1 w-full rounded border border-paper-line bg-paper px-3 py-3";

  return (
    <div className="mx-auto max-w-5xl px-5 py-10">
      <h1 className="text-3xl font-semibold">Books</h1>
      {/* Plain GET form: works without JavaScript on any phone. */}
      <form method="get" className="mt-6 grid gap-3 sm:grid-cols-4" role="search">
        <label className="sm:col-span-4 text-sm">Search
          <input name="q" defaultValue={q} className={field} placeholder="Title or topic" maxLength={100} />
        </label>
        <label className="text-sm">Subject
          <select name="subject" defaultValue={subject ?? ""} className={field}>
            <option value="">All</option>{opts.subjects.map((s) => <option key={s}>{s}</option>)}
          </select>
        </label>
        <label className="text-sm">Level
          <select name="level" defaultValue={level ?? ""} className={field}>
            <option value="">All</option>{opts.levels.map((s) => <option key={s}>{s}</option>)}
          </select>
        </label>
        <label className="text-sm">Format
          <select name="format" defaultValue={format ?? ""} className={field}>
            <option value="">All</option><option value="PHYSICAL">Physical</option><option value="DIGITAL">Digital</option>
          </select>
        </label>
        <div className="flex items-end gap-3">
          <button className="rounded bg-navy-900 px-5 py-3 text-paper hover:bg-navy-800">Search</button>
          {filtered && <a href="/books" className="py-3 text-sm underline">Clear</a>}
        </div>
      </form>

      <p className="mt-6 text-sm text-ink-muted" aria-live="polite">{books.length} {books.length === 1 ? "book" : "books"}</p>
      {books.length ? (
        <div className="mt-3 grid gap-4">{books.map((b) => <BookCard key={b.id} book={b} />)}</div>
      ) : (
        <p className="mt-3 rounded border border-paper-line bg-paper p-5">
          {filtered ? "No books match those filters. Try clearing them." : "No books are published yet."}
        </p>
      )}
    </div>
  );
}
