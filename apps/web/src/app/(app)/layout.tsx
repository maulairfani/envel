import { AppShell } from "@/components/layout/app-shell";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { ChatNavProvider } from "@/features/chat/chat-nav";

/** Authenticated app frame: shared sidebar (chat + nav) around every page. */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ChatNavProvider>
      <AppShell sidebar={<AppSidebar />}>{children}</AppShell>
    </ChatNavProvider>
  );
}
