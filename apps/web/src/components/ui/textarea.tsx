import { cn, focusRing } from "@/lib/utils";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  ref?: React.Ref<HTMLTextAreaElement>;
}

export function Textarea({ className, ref, ...props }: TextareaProps) {
  return (
    <textarea
      ref={ref}
      className={cn(
        "flex min-h-20 w-full resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm",
        "placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",
        focusRing,
        className,
      )}
      {...props}
    />
  );
}
