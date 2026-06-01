import { cn } from "@/lib/utils";

/**
 * Envel logo mark — an open envelope / wallet drawn as strokes so it inherits
 * `currentColor` (lime on dark, ink on light). Approximates the brand mark.
 */
export function LogoMark({ className, ...props }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 48 40"
      fill="none"
      stroke="currentColor"
      strokeWidth={4.25}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={cn("size-6", className)}
      {...props}
    >
      {/* flap: left-top → center dip → right-top */}
      <path d="M5 6 L24 22 L43 6" />
      {/* bowl: open container with rounded bottom */}
      <path d="M9 13 V27 a6 6 0 0 0 6 6 H33 a6 6 0 0 0 6 -6 V13" />
    </svg>
  );
}

export interface LogoProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Hide the wordmark, show only the mark. */
  markOnly?: boolean;
}

/** Full lockup: mark + "envel" wordmark. Inherits text color. */
export function Logo({ markOnly = false, className, ...props }: LogoProps) {
  return (
    <div className={cn("inline-flex items-center gap-2 text-foreground", className)} {...props}>
      <LogoMark className="size-7" />
      {!markOnly && (
        <span className="text-xl font-semibold lowercase tracking-tight">envel</span>
      )}
    </div>
  );
}
