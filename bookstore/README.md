# Kigundu Books (foundation, step 1 of 5)

Next.js 14 + TypeScript + Tailwind + Prisma/Postgres.

## Status
Done: project config, Prisma schema, core logic (UGX money, Uganda phone validation, order maths,
rate limiter, slugs), design tokens, branded 404, robots, non-destructive seed.
Not done yet: public pages, catalogue, checkout, admin UI and auth, sitemap, images, email.

## Setup
1. `npm install`
2. `cp .env.example .env` and fill it in (use a pooled DB URL for `DATABASE_URL`, direct for `DIRECT_URL`).
3. `npx prisma migrate dev --name init` (first time; creates migration files to commit).
4. `npm run db:seed` creates the first admin and a DRAFT book. Never run against a DB you can't afford to touch without a backup.
5. `npm run dev`

## Checks
`npm run typecheck` · `npm test` · `npm run build`

## Owner must confirm before launch
Author name spelling, brand name, prices, ISBN, stock, contact details, WhatsApp number, payment instructions,
delivery zones and fees, policy text (needs legal review), a clean front-cover scan.
