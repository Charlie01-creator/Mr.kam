import type { Prisma } from "@prisma/client";
import { db } from "./db.ts";

const publicInclude = { author: true, images: { orderBy: { sortOrder: "asc" } } } satisfies Prisma.BookInclude;
export type PublicBook = Prisma.BookGetPayload<{ include: typeof publicInclude }>;

export interface CatalogueFilters { q?: string; subject?: string; level?: string; format?: "PHYSICAL" | "DIGITAL" }

export async function listPublishedBooks(f: CatalogueFilters = {}): Promise<PublicBook[]> {
  const where: Prisma.BookWhereInput = { status: "PUBLISHED" };
  if (f.subject) where.subject = f.subject;
  if (f.level) where.level = f.level;
  if (f.format) where.format = f.format;
  if (f.q) {
    where.OR = [
      { title: { contains: f.q, mode: "insensitive" } },
      { subtitle: { contains: f.q, mode: "insensitive" } },
      { summary: { contains: f.q, mode: "insensitive" } },
      { subject: { contains: f.q, mode: "insensitive" } },
    ];
  }
  return db.book.findMany({ where, include: publicInclude, orderBy: { createdAt: "desc" }, take: 60 });
}

export function getPublishedBook(slug: string) {
  return db.book.findFirst({ where: { slug, status: "PUBLISHED" }, include: publicInclude });
}

export async function relatedBooks(book: { id: string; subject: string | null }) {
  return db.book.findMany({
    where: { status: "PUBLISHED", id: { not: book.id }, ...(book.subject ? { subject: book.subject } : {}) },
    include: publicInclude, take: 3, orderBy: { createdAt: "desc" },
  });
}

export async function filterOptions() {
  const rows = await db.book.findMany({ where: { status: "PUBLISHED" }, select: { subject: true, level: true } });
  const uniq = (xs: (string | null)[]) => [...new Set(xs.filter((x): x is string => !!x))].sort();
  return { subjects: uniq(rows.map((r) => r.subject)), levels: uniq(rows.map((r) => r.level)) };
}

/** Availability only when the owner has actually set stock. Unknown stays unknown. */
export function availability(b: { stock: number | null; priceUgx: number | null }): "in_stock" | "out_of_stock" | "enquire" {
  if (b.priceUgx == null || b.stock == null) return "enquire";
  return b.stock > 0 ? "in_stock" : "out_of_stock";
}
