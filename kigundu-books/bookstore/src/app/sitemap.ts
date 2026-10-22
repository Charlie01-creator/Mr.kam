import type { MetadataRoute } from "next";
import { db } from "@/lib/db";

export const dynamic = "force-dynamic";
const base = process.env.SITE_URL ?? "http://localhost:3000";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [books, policies] = await Promise.all([
    db.book.findMany({ where: { status: "PUBLISHED" }, select: { slug: true, updatedAt: true } }),
    db.policy.findMany({ where: { published: true, reviewed: true }, select: { slug: true, updatedAt: true } }),
  ]);
  return [
    ...["", "/books", "/about", "/faq"].map((p) => ({ url: `${base}${p}` })),
    ...books.map((b) => ({ url: `${base}/books/${b.slug}`, lastModified: b.updatedAt })),
    ...policies.map((p) => ({ url: `${base}/policies/${p.slug}`, lastModified: p.updatedAt })),
  ];
}
