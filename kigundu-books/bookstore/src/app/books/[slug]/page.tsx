import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { availability, getPublishedBook, relatedBooks } from "@/lib/books";
import { formatUgx } from "@/lib/money";
import { BookCover } from "@/components/BookCover";
import { BookCard } from "@/components/BookCard";

export const dynamic = "force-dynamic";
const base = process.env.SITE_URL ?? "http://localhost:3000";

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const b = await getPublishedBook(params.slug);
  if (!b) return { title: "Book not found", robots: { index: false } };
  const desc = (b.summary ?? b.description ?? `${b.title} by ${b.author.name}.`).slice(0, 160);
  return {
    title: b.title, description: desc,
    alternates: { canonical: `/books/${b.slug}` },
    openGraph: { type: "book", title: b.title, description: desc, url: `${base}/books/${b.slug}`, images: b.images[0] ? [b.images[0].url] : [] },
  };
}

export default async function BookPage({ params }: { params: { slug: string } }) {
  const b = await getPublishedBook(params.slug);
  if (!b) notFound();
  const related = await relatedBooks(b);
  const avail = availability(b);

  // Offer data only when the owner has set a real price; availability only when stock is known.
  const jsonLd = {
    "@context": "https://schema.org", "@type": "Book",
    name: b.title, author: { "@type": "Person", name: b.author.name },
    url: `${base}/books/${b.slug}`,
    ...(b.isbn && { isbn: b.isbn }),
    ...(b.edition && { bookEdition: b.edition }),
    ...(b.images[0] && { image: b.images[0].url }),
    ...(b.priceUgx != null && {
      offers: {
        "@type": "Offer", priceCurrency: "UGX", price: b.priceUgx,
        ...(avail !== "enquire" && { availability: avail === "in_stock" ? "https://schema.org/InStock" : "https://schema.org/OutOfStock" }),
      },
    }),
  };

  const facts: [string, string | number | null][] = [
    ["Author", b.author.name], ["Subject", b.subject], ["Level", b.level], ["Audience", b.audience],
    ["Edition", b.edition], ["Published", b.publicationYear], ["ISBN", b.isbn],
    ["Format", b.format === "DIGITAL" ? "Digital" : "Physical"],
  ];

  return (
    <div className="mx-auto max-w-5xl px-5 py-10">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <div className="grid gap-8 sm:grid-cols-[260px_1fr]">
        <div className="w-48 sm:w-full"><BookCover title={b.title} image={b.images[0]} priority /></div>
        <div>
          <h1 className="text-3xl font-semibold leading-tight">{b.title}</h1>
          {b.subtitle && <p className="mt-1 text-lg text-ink-muted">{b.subtitle}</p>}
          <p className="mt-4 text-2xl font-semibold">{b.priceUgx != null ? formatUgx(b.priceUgx) : "Price on request"}</p>
          <p className="mt-1 text-sm text-ink-muted">
            {{ in_stock: "In stock", out_of_stock: "Out of stock", enquire: "Contact us to confirm availability" }[avail]}
          </p>
          {/* Order button and quantity selector arrive with checkout in step 3. */}
          <dl className="mt-6 grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
            {facts.filter(([, v]) => v != null && v !== "").map(([k, v]) => (
              <div key={k} className="contents"><dt className="text-ink-muted">{k}</dt><dd>{v}</dd></div>
            ))}
          </dl>
        </div>
      </div>

      {b.description && <section className="mt-10" aria-labelledby="d-h"><h2 id="d-h" className="text-xl font-semibold">About this book</h2>
        <p className="mt-2 max-w-prose whitespace-pre-line">{b.description}</p></section>}
      {b.tableOfContents && <section className="mt-8" aria-labelledby="t-h"><h2 id="t-h" className="text-xl font-semibold">Contents</h2>
        <p className="mt-2 max-w-prose whitespace-pre-line">{b.tableOfContents}</p></section>}

      {related.length > 0 && <section className="mt-12" aria-labelledby="r-h"><h2 id="r-h" className="text-xl font-semibold">Related books</h2>
        <div className="mt-4 grid gap-4">{related.map((r) => <BookCard key={r.id} book={r} />)}</div></section>}
    </div>
  );
}
