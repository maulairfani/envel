import { Logo } from "@/components/brand/logo";
import { Button, Input, Label } from "@/components/ui";

const ERRORS: Record<string, string> = {
  invalid: "Username atau password salah.",
  unavailable: "Server auth tidak bisa dihubungi. Coba lagi nanti.",
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;

  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-8 px-6">
      <Logo />
      <form
        method="post"
        action="/api/auth/login"
        className="w-full max-w-sm space-y-4"
      >
        <div className="space-y-1 text-center">
          <h1 className="text-lg font-semibold">Masuk ke Envel</h1>
          <p className="text-sm text-muted-foreground">
            Kelola anggaran lewat percakapan.
          </p>
        </div>

        {error && (
          <p className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {ERRORS[error] ?? "Terjadi kesalahan saat login."}
          </p>
        )}

        <div className="space-y-2">
          <Label htmlFor="username">Username</Label>
          <Input id="username" name="username" autoComplete="username" autoFocus required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
        </div>

        <Button type="submit" className="w-full">
          Masuk
        </Button>
      </form>
    </main>
  );
}
