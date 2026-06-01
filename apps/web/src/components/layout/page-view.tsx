/** Scrollable page scaffold for the non-chat app pages (header + content). */
export function PageView({
  title,
  action,
  children,
}: {
  title: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-2xl px-6 py-8">
        <header className="mb-6 flex items-end justify-between gap-4">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          {action}
        </header>
        {children}
      </div>
    </div>
  );
}
