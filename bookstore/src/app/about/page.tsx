import type { Metadata } from "next";
import { getContent } from "@/lib/content";
import { site } from "@/config/site";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "About the author", description: `About ${site.author.name}, mathematics teacher and textbook author.`, alternates: { canonical: "/about" } };

const sections = [
  ["about.bio", "Biography"], ["about.teaching", "Teaching experience"], ["about.philosophy", "Educational philosophy"],
  ["about.works", "Published works"], ["about.credentials", "Credentials"],
] as const;

export default async function About() {
  const entries = await Promise.all(sections.map(async ([k, h]) => [h, await getContent(k)] as const));
  const filled = entries.filter(([, v]) => v);
  return (
    <div className="mx-auto max-w-3xl px-5 py-10">
      <h1 className="text-3xl font-semibold">{site.author.name}</h1>
      {filled.length ? filled.map(([h, v]) => (
        <section key={h} className="mt-8"><h2 className="text-xl font-semibold">{h}</h2><p className="mt-2 whitespace-pre-line">{v}</p></section>
      )) : <p className="mt-4 text-ink-muted">The author's profile is being prepared.</p>}
    </div>
  );
}
