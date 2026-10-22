import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { db } from "@/lib/db";

export const dynamic = "force-dynamic";
const get = (slug: string) => db.policy.findFirst({ where: { slug, published: true, reviewed: true } });

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const p = await get(params.slug);
  return p ? { title: p.title, alternates: { canonical: `/policies/${p.slug}` } } : { title: "Not found", robots: { index: false } };
}

export default async function PolicyPage({ params }: { params: { slug: string } }) {
  const p = await get(params.slug);
  if (!p) notFound(); // unreviewed policy text is never shown publicly
  return (
    <div className="mx-auto max-w-3xl px-5 py-10">
      <h1 className="text-3xl font-semibold">{p.title}</h1>
      <p className="mt-6 whitespace-pre-line">{p.body}</p>
    </div>
  );
}
