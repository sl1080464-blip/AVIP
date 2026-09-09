"use client";

import { useEffect, useState } from "react";

type Camera = {
  id: number;
  name: string;
  status: string;
};

type Alert = {
  id: number;
  level: string;
  message: string;
  acknowledged: boolean;
};

const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const apiRoot = configuredApiUrl.endsWith("/api/v1")
  ? configuredApiUrl
  : `${configuredApiUrl.replace(/\/$/, "")}/api/v1`;

export default function HomePage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [detectionCount, setDetectionCount] = useState(0);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const responses = await Promise.all([
          fetch(`${apiRoot}/cameras`),
          fetch(`${apiRoot}/detections`),
          fetch(`${apiRoot}/alerts`),
        ]);
        if (responses.some((response) => !response.ok)) {
          throw new Error("The AVIP API returned an error.");
        }
        const [cameraData, detectionData, alertData] = await Promise.all(
          responses.map((response) => response.json()),
        );
        setCameras(cameraData);
        setDetectionCount(detectionData.length);
        setAlerts(alertData);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load dashboard data.");
      }
    }

    void loadDashboard();
  }, []);

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
            { title: "Cameras", value: cameras.length.toString() },
            { title: "Detections", value: detectionCount.toString() },
            { title: "Alerts", value: alerts.filter((alert) => !alert.acknowledged).length.toString() },
          ].map((card) => (
            <div key={card.title} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">{card.title}</p>
              <p className="mt-2 text-3xl font-semibold">{card.value}</p>
            </div>
          ))}
        </div>

        {error ? (
          <p className="mt-8 rounded-xl border border-amber-400/30 bg-amber-400/10 p-4 text-amber-200">
            {error}
          </p>
        ) : null}

        <section className="mt-10 rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="text-lg font-semibold">Cameras</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {cameras.map((camera) => (
              <div key={camera.id} className="flex items-center justify-between rounded-xl bg-slate-800/70 p-4">
                <span>{camera.name}</span>
                <span className="text-sm text-emerald-300">{camera.status}</span>
              </div>
            ))}
            {cameras.length === 0 && !error ? (
              <p className="text-sm text-slate-400">No cameras registered.</p>
            ) : null}
          </div>
        </section>
      </div>
    </main>
  );
}
