import { cn } from "@/lib/utils";
import {
  formatIDR,
  formatIDRPlain,
  resolveMoneyTone,
  type MoneyTone,
} from "@/lib/format";

const toneClass: Record<Exclude<MoneyTone, "auto">, string> = {
  neutral: "text-foreground",
  positive: "text-positive",
  negative: "text-negative",
};

export interface MoneyTextProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** IDR integer (no decimals). */
  amount: number;
  /** "auto" colors by sign; force a tone otherwise. Default: neutral. */
  tone?: MoneyTone;
  /** Drop the "Rp" symbol (dense tables). */
  plain?: boolean;
  /** Prefix "+" on positive amounts. */
  showSign?: boolean;
}

/** Tabular IDR amount with sign-aware coloring. The money primitive. */
export function MoneyText({
  amount,
  tone = "neutral",
  plain = false,
  showSign = false,
  className,
  ...props
}: MoneyTextProps) {
  const resolved = resolveMoneyTone(amount, tone);
  const formatted = plain ? formatIDRPlain(Math.abs(amount)) : formatIDR(Math.abs(amount));
  const sign = amount < 0 ? "−" : showSign && amount > 0 ? "+" : "";

  return (
    <span
      className={cn("font-numeric tabular-nums", toneClass[resolved], className)}
      {...props}
    >
      {sign}
      {formatted}
    </span>
  );
}
