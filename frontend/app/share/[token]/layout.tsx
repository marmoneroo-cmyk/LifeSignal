/**
 * Bare layout for public shared report pages — bypasses the AuthGate from the
 * root layout by NOT rendering its children there. The root layout always wraps
 * children with AuthGate, so we shadow it for this route segment with a
 * minimal layout that just renders its children inside a clean container.
 *
 * Auth is intentionally not required here: the public report is gated by the
 * unguessable token in the URL, which the backend validates and expires.
 */
export default function SharedReportLayout({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen bg-slate-50">{children}</div>;
}
