import Link from "next/link";
import { site } from "@/config/site";

const nav = [
  { href: "/books", label: "Books" },
  { href: "/about", label: "About the author" },
  { href: "/faq", label: "FAQ" },
];

export function Header() {
  return (
    <header className="border-b border-paper-line bg-paper">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-5 py-3">
        <Link href="/" className="font-serif text-xl font-semibold text-navy-900">{site.name}</Link>
        <nav aria-label="Main"><ul className="flex gap-5 text-sm">
          {nav.map((n) => <li key={n.href}><Link href={n.href} className="py-2 hover:underline">{n.label}</Link></li>)}
        </ul></nav>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="mt-20 border-t border-paper-line bg-navy-950 text-paper/80">
      <div className="mx-auto flex max-w-5xl flex-wrap justify-between gap-6 px-5 py-8 text-sm">
        <p>{site.name}. Books by {site.author.name}.</p>
        <nav aria-label="Policies"><ul className="flex flex-wrap gap-4">
          {[["privacy", "Privacy"], ["terms", "Terms of sale"], ["returns", "Returns"], ["delivery", "Delivery"]].map(([s, l]) =>
            <li key={s}><Link href={`/policies/${s}`} className="py-2 hover:underline">{l}</Link></li>)}
        </ul></nav>
      </div>
    </footer>
  );
}
