import Link from "next/link";
import type { PublicBook } from "@/lib/books";
import { availability } from "@/lib/books";
import { formatUgx } from "@/lib/money";
import { BookCover } from "./BookCover";

const label = { in_stock: "In stock", out_of_stock: "Out of stock", enquire: "Ask about availability" } as const;

export function BookCard({ book }: { book: PublicBook }) {
  const img = book.images[0];
  return (
    <article className="flex gap-4 rounded border border-paper-line bg-paper p-4 hover:border-gold">
      <div className="w-24 shrink-0 sm:w-32"><BookCover title={book.title} image={img} /></div>
      <div className="min-w-0">
        <h3 className="text-lg font-semibold leading-snug">
          <Link href={`/books/${book.slug}`} className="hover:underline">{book.title}</Link>
        </h3>
        <p className="mt-1 text-sm text-ink-muted">{book.author.name}</p>
        {(book.subject || book.level) && <p className="mt-1 text-sm">{[book.subject, book.level].filter(Boolean).join(", ")}</p>}
        {book.summary && <p className="mt-2 line-clamp-3 text-sm text-ink-muted">{book.summary}</p>}
        <p className="mt-3 text-sm font-medium">
          {book.priceUgx != null ? formatUgx(book.priceUgx) : "Price on request"}
          <span className="ml-2 font-normal text-ink-muted">{label[availability(book)]}</span>
        </p>
      </div>
    </article>
  );
}
