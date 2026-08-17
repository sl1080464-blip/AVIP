export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <span className="inline-flex rounded-full border border-cyan-400/40 bg-cyan-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-cyan-300">
          AVIP
        </span>

        <h1 className="mt-8 text-4xl font-bold tracking-tight sm:text-6xl">
          AI Vision Intelligence Platform
        </h1>

        <p className="mt-6 max-w-2xl text-lg text-slate-300">
          Modular video intelligence, event-driven monitoring, and risk-aware surveillance workflows.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-3">
          {[
            { title: "Cameras", value: "0" },
            { title: "Detections", value: "0" },
            { title: "Alerts", value: "0" },
          ].map((card) => (
            <div key={card.title} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">{card.title}</p>
              <p className="mt-2 text-3xl font-semibold">{card.value}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
