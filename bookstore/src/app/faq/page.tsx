import type { Metadata } from "next";
import { db } from "@/lib/db";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Frequently asked questions", description: "Ordering, payment, delivery and bulk purchases.", alternates: { canonical: "/faq" } };

export default async function Faq() {
  const faqs = await db.faq.findMany({ where: { published: true }, orderBy: { sortOrder: "asc" } });
  return (
    <div className="mx-auto max-w-3xl px-5 py-10">
      <h1 className="text-3xl font-semibold">Frequently asked questions</h1>
      {faqs.length ? faqs.map((f) => (
        <details key={f.id} className="mt-3 rounded border border-paper-line bg-paper p-4">
          <summary className="cursor-pointer font-medium">{f.question}</summary>
          <p className="mt-2 whitespace-pre-line text-ink-muted">{f.answer}</p>
        </details>
      )) : <p className="mt-4 text-ink-muted">Answers are being added. For now, contact us with your question.</p>}
    </div>
  );
}
