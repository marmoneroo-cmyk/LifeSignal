"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  LayoutDashboard,
  FlaskConical,
  ShieldCheck,
  FileText,
  Clock,
  Upload,
  Pill,
  Users,
  MessageCircleQuestion,
  Sparkles,
  Target,
  Link2,
  GitCompare,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import { LangToggle } from "@/components/LangToggle";

export function Sidebar() {
  const pathname = usePathname();
  const { t } = useT();

  const NAV = [
    { href: "/",            label: t("nav.dashboard"), icon: LayoutDashboard },
    { href: "/report",      label: t("nav.report"),    icon: FileText },
    { href: "/chat",        label: t("nav.chat"),      icon: Sparkles },
    { href: "/copilot",     label: t("nav.copilot"),   icon: MessageCircleQuestion },
    { href: "/timeline",    label: t("nav.timeline"),  icon: Clock },
    { href: "/compare",     label: t("nav.compare"),   icon: GitCompare },
    { href: "/upload",      label: t("nav.upload"),    icon: Upload },
    { href: "/labs",        label: t("nav.labs"),      icon: FlaskConical },
    { href: "/insurance",   label: t("nav.insurance"), icon: ShieldCheck },
    { href: "/medications", label: t("nav.medications"), icon: Pill },
    { href: "/family",      label: t("nav.family"),    icon: Users },
    { href: "/goals",       label: t("nav.goals"),     icon: Target },
    { href: "/share",       label: t("nav.share"),     icon: Link2 },
  ];

  return (
    <aside className="flex w-60 shrink-0 flex-col border-e border-slate-200 bg-white print:hidden">
      <div className="flex items-center gap-2 px-5 py-5">
        <Activity className="h-6 w-6 text-brand" />
        <span className="text-lg font-bold text-slate-800">{t("app.name")}</span>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium",
                active
                  ? "bg-brand-soft text-brand-fg"
                  : "text-slate-600 hover:bg-slate-100",
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-5 pb-4 space-y-3">
        <LangToggle />
        <p className="text-[10px] leading-tight text-slate-400">{t("sidebar.disclaimer")}</p>
      </div>
    </aside>
  );
}
