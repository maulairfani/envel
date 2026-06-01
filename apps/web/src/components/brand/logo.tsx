import Image from "next/image";
import { cn } from "@/lib/utils";

/**
 * Envel wordmark lockup (lime, transparent bg) — used in the header only.
 * Source art cropped + recolored from brand/dark-horizontal-lockup.png.
 */
export function Logo({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span className={cn("inline-flex items-center", className)} {...props}>
      <Image
        src="/brand/lockup-lime.png"
        alt="Envel"
        width={854}
        height={226}
        priority
        className="h-7 w-auto"
      />
    </span>
  );
}
