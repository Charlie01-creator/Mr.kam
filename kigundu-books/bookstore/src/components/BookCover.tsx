import Image from "next/image";

interface Props { title: string; image?: { url: string; alt: string } | undefined; priority?: boolean }

/** Real cover if uploaded; otherwise a plainly labelled stand-in, never the damaged reference photo. */
export function BookCover({ title, image, priority }: Props) {
  if (image) {
    return (
      <Image src={image.url} alt={image.alt} width={300} height={420} priority={priority}
        sizes="(max-width: 640px) 60vw, 300px" className="aspect-[5/7] w-full rounded-sm border border-paper-line object-cover shadow-md" />
    );
  }
  return (
    <div role="img" aria-label={`Cover image for ${title} not yet uploaded`}
      className="flex aspect-[5/7] w-full flex-col justify-between rounded-sm border border-paper-line bg-navy-900 p-4 text-paper shadow-md">
      <span className="font-serif text-lg font-semibold leading-snug text-gold-soft">{title}</span>
      <span className="text-xs text-paper/70">Cover image coming soon</span>
    </div>
  );
}
