import Link from "next/link";
import { listPublishedBooks } from "@/lib/books";
import { getContent } from "@/lib/content";
import { site } from "@/config/site";
import { BookCover } from "@/components/BookCover";
import { BookCard } from "@/components/BookCard";

export const dynamic = "force-dynamic";

const audiences = [
  { h: "Students", p: "Worked topics in statistics and numerical methods to revise from alongside your class notes." },
  { h: "Teachers", p: "A classroom reference by a practising mathematics teacher." },
  { h: "Schools", p: "Order copies for a class or a library, with a written quotation." },
  { h: "Bookshops and institutions", p: "Ask for bulk pricing on any title in the catalogue." },
];

export default async function Home() {
  const books = await listPublishedBooks();
  const featured = books[0];
  const intro = await getContent("home.intro", `${site.name} publishes mathematics textbooks by ${site.author.name}.`);
  const mission = await getContent("home.mission", "");

  return (
    <>
      <section className="bg-navy-950 text-paper">
        <div className="mx-auto grid max-w-5xl items-center gap-10 px-5 py-14 sm:grid-cols-[1fr_220px]">
          <div>
            <h1 className="max-w-xl text-3xl font-semibold leading-tight text-paper sm:text-5xl">
              Practical mathematics resources for students and educators
            </h1>
            <p className="mt-4 max-w-prose text-paper/80">{intro}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/books" className="rounded bg-gold px-5 py-3 font-medium text-navy-950 hover:bg-gold-soft">Explore books</Link>
              <Link href={featured ? `/books/${featured.slug}` : "/books"} className="rounded border border-paper/60 px-5 py-3 hover:bg-navy-800">Order a book</Link>
            </div>
          </div>
          {featured && <div className="w-40 sm:w-full"><BookCover title={featured.title} image={featured.images[0]} priority /></div>}
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-5 pt-14" aria-labelledby="featured-h">
        <h2 id="featured-h" className="text-2xl font-semibold">Featured book</h2>
        {featured ? (
          <div className="mt-5"><BookCard book={featured} /></div>
        ) : (
          <p className="mt-4 rounded border border-paper-line bg-paper p-5 text-ink-muted">
            The first title is being prepared for sale. Check back soon.
          </p>
        )}
      </section>

      <section className="mx-auto max-w-5xl px-5 pt-14" aria-labelledby="who-h">
        <h2 id="who-h" className="text-2xl font-semibold">Who the books are for</h2>
        <dl className="mt-5 grid gap-4 sm:grid-cols-2">
          {audiences.map((a) => (
            <div key={a.h} className="rounded border border-paper-line bg-paper p-5">
              <dt className="font-serif text-lg font-semibold text-navy-900">{a.h}</dt>
              <dd className="mt-1 text-sm text-ink-muted">{a.p}</dd>
            </div>
          ))}
        </dl>
      </section>

      {mission && (
        <section className="mx-auto max-w-5xl px-5 pt-14" aria-labelledby="mission-h">
          <h2 id="mission-h" className="text-2xl font-semibold">Why these books exist</h2>
          <p className="mt-3 max-w-prose">{mission}</p>
        </section>
      )}
    </>
  );
}
