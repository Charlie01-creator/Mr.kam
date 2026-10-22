import { db } from "./db.ts";

/** Editable copy from the admin dashboard, with a safe default. */
export async function getContent(key: string, fallback = ""): Promise<string> {
  const row = await db.siteContent.findUnique({ where: { key } });
  return row?.value ?? fallback;
}
