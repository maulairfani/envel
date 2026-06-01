import Link from "next/link";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui";

export default function Home() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-8 px-6 text-center">
      <Logo className="scale-125" />
      <p className="max-w-md text-balance text-muted-foreground">
        Conversational envelope budgeting. Setiap rupiah punya tujuan.
      </p>
      <Button asChild variant="outline">
        <Link href="/styleguide">Lihat design system →</Link>
      </Button>
    </main>
  );
}
