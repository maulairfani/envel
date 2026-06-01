"use client";

import { useState } from "react";
import { Moon, Sun, Plus, ArrowRight, Trash2 } from "lucide-react";
import {
  Button,
  Input,
  Textarea,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Badge,
  Label,
  Skeleton,
  Separator,
  Spinner,
  Avatar,
  MoneyText,
} from "@/components/ui";
import { Logo } from "@/components/brand/logo";
import { MessageBubble } from "@/features/chat";
import type { ChatMessage } from "@/features/chat";

const SWATCHES = [
  ["background", "bg-background border border-border"],
  ["surface", "bg-surface"],
  ["surface-2", "bg-surface-2"],
  ["primary", "bg-primary"],
  ["secondary", "bg-secondary"],
  ["muted", "bg-muted"],
  ["border", "bg-border"],
  ["positive", "bg-positive"],
  ["negative", "bg-negative"],
  ["warning", "bg-warning"],
] as const;

const TYPE_SCALE = [
  ["Display", "text-4xl font-semibold tracking-tight"],
  ["Heading", "text-2xl font-semibold tracking-tight"],
  ["Title", "text-lg font-semibold"],
  ["Body", "text-sm"],
  ["Label", "text-xs font-medium uppercase tracking-wide text-muted-foreground"],
] as const;

const DEMO_MESSAGES: ChatMessage[] = [
  { id: "1", role: "user", content: "How much of my food budget is left this month?" },
  {
    id: "2",
    role: "assistant",
    content:
      "The “Food” envelope still has Rp420.000 left of the Rp1.500.000 you assigned this month.",
    toolCalls: [
      {
        id: "t1",
        name: "get_workspace",
        status: "success",
        args: { period: "2026-06" },
        result: { envelope: "Food", assigned: 1500000, activity: 1080000, available: 420000 },
      },
    ],
  },
];

export default function StyleguidePage() {
  const [dark, setDark] = useState(true);

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <header className="mb-12 flex items-center justify-between">
        <div>
          <Logo className="mb-3" />
          <p className="text-sm text-muted-foreground">Design system — tokens & components</p>
        </div>
        <Button variant="outline" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          {dark ? <Sun /> : <Moon />}
        </Button>
      </header>

      <div className="space-y-14">
        <Section title="Brand">
          <div className="flex flex-wrap items-center gap-8 rounded-lg border border-border bg-surface p-6">
            <Logo />
            <span className="text-xs text-muted-foreground">
              Wordmark lockup — header only
            </span>
          </div>
        </Section>

        <Section title="Color">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            {SWATCHES.map(([name, cls]) => (
              <div key={name} className="space-y-1.5">
                <div className={`h-16 rounded-md ${cls}`} />
                <div className="text-xs text-muted-foreground">{name}</div>
              </div>
            ))}
          </div>
        </Section>

        <Section title="Typography — General Sans">
          <div className="space-y-3">
            {TYPE_SCALE.map(([name, cls]) => (
              <div key={name} className="flex items-baseline gap-4">
                <span className="w-20 shrink-0 text-xs text-muted-foreground">{name}</span>
                <span className={cls}>Every rupiah has a purpose</span>
              </div>
            ))}
            <div className="flex items-baseline gap-4">
              <span className="w-20 shrink-0 text-xs text-muted-foreground">Numeric</span>
              <span className="font-numeric text-lg tabular-nums">Rp1.250.000 · 2026-06</span>
            </div>
          </div>
        </Section>

        <Section title="Buttons">
          <div className="flex flex-wrap gap-3">
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <Button size="sm">Small</Button>
            <Button size="md">Medium</Button>
            <Button size="lg">Large</Button>
            <Button size="icon" aria-label="Add">
              <Plus />
            </Button>
            <Button loading>Loading</Button>
            <Button disabled>Disabled</Button>
            <Button>
              Continue <ArrowRight />
            </Button>
          </div>
        </Section>

        <Section title="Badges">
          <div className="flex flex-wrap gap-2">
            <Badge>Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="outline">Outline</Badge>
            <Badge variant="positive">Income</Badge>
            <Badge variant="negative">Over budget</Badge>
            <Badge variant="warning">Due soon</Badge>
          </div>
        </Section>

        <Section title="Forms">
          <div className="grid max-w-md gap-4">
            <div className="space-y-2">
              <Label htmlFor="sg-name">Envelope name</Label>
              <Input id="sg-name" placeholder="e.g. Food" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sg-note">Note</Label>
              <Textarea id="sg-note" placeholder="Write something…" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sg-err">With error</Label>
              <Input id="sg-err" aria-invalid defaultValue="invalid" />
            </div>
          </div>
        </Section>

        <Section title="Money">
          <div className="flex flex-wrap items-center gap-6 text-lg">
            <MoneyText amount={1250000} />
            <MoneyText amount={2500000} tone="auto" showSign />
            <MoneyText amount={-480000} tone="auto" />
            <MoneyText amount={420000} tone="positive" />
            <MoneyText amount={150000} plain />
          </div>
        </Section>

        <Section title="Card">
          <Card className="max-w-sm">
            <CardHeader>
              <CardTitle>Food</CardTitle>
              <CardDescription>Spend monthly · target Rp1.500.000</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Remaining</span>
              <MoneyText amount={420000} tone="positive" className="text-base" />
            </CardContent>
          </Card>
        </Section>

        <Section title="Chat patterns">
          <div className="space-y-5 rounded-lg border border-border bg-surface p-5">
            {DEMO_MESSAGES.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
          </div>
        </Section>

        <Section title="Feedback">
          <div className="flex flex-wrap items-center gap-6">
            <Spinner />
            <Avatar fallback="MA" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          </div>
          <Separator className="my-6" />
          <p className="text-xs text-muted-foreground">Separator above.</p>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="mb-5 text-xs font-medium uppercase tracking-wider text-muted-foreground">
        {title}
      </h2>
      {children}
    </section>
  );
}
