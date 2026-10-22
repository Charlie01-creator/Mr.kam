import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";
import { site, knownBook } from "../src/config/site.ts";

const db = new PrismaClient();

async function main() {
  const email = process.env.SEED_ADMIN_EMAIL;
  const password = process.env.SEED_ADMIN_PASSWORD;
  if (!email || !password || password.length < 12) {
    throw new Error("Set SEED_ADMIN_EMAIL and a SEED_ADMIN_PASSWORD of 12+ characters.");
  }
  // Non-destructive: upserts only, never deletes.
  await db.user.upsert({
    where: { email },
    update: {},
    create: { email, role: "ADMIN", passwordHash: await bcrypt.hash(password, 12) },
  });

  const author = (await db.author.findFirst({ where: { name: site.author.name } }))
    ?? (await db.author.create({ data: { name: site.author.name, verified: site.author.verified } }));

  await db.book.upsert({
    where: { slug: knownBook.slug },
    update: {},
    create: {
      slug: knownBook.slug,
      title: knownBook.title,
      edition: knownBook.edition,
      authorId: author.id,
      status: "DRAFT", // stays unpublished until the owner verifies and publishes
      verifiedFields: [...knownBook.verifiedFields],
      isTemporaryCover: true,
    },
  });
  console.log("Seed complete (admin + draft book).");
}

main().finally(() => db.$disconnect());
