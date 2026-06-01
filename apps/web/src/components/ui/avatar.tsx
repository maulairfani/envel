import { cn } from "@/lib/utils";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Initials or short label shown when there is no image. */
  fallback?: string;
}

/** Minimal avatar — initials fallback only (no image deps yet). */
export function Avatar({ className, fallback, children, ...props }: AvatarProps) {
  return (
    <div
      className={cn(
        "flex size-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-surface-2 text-xs font-medium text-muted-foreground",
        className,
      )}
      {...props}
    >
      {children ?? fallback}
    </div>
  );
}
