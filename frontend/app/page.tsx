"use client";

import { useEffect, useState, type FormEvent } from "react";

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

type CurrentUser = {
  id: number;
  username: string;
  email: string;
};

const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const apiRoot = configuredApiUrl.endsWith("/api/v1")
  ? configuredApiUrl
  : `${configuredApiUrl.replace(/\/$/, "")}/api/v1`;

export default function HomePage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [detectionCount, setDetectionCount] = useState(0);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = window.sessionStorage.getItem("avip_access_token");

    async function loadDashboard() {
      try {
        const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
        const responses = await Promise.all([
          fetch(`${apiRoot}/cameras`, { headers }),
          fetch(`${apiRoot}/detections`, { headers }),
          fetch(`${apiRoot}/alerts`, { headers }),
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

    async function loadCurrentUser() {
      if (!token) return;
      const response = await fetch(`${apiRoot}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        setCurrentUser(await response.json());
      } else {
        window.sessionStorage.removeItem("avip_access_token");
      }
    }

    void loadDashboard();
    void loadCurrentUser();
  }, []);

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthError(null);
    setIsSigningIn(true);
    try {
      const response = await fetch(`${apiRoot}/auth/${authMode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          authMode === "register" ? { username, email, password } : { username, password },
        ),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        const detail = typeof body?.detail === "string" ? body.detail : null;
        throw new Error(detail ?? (authMode === "register" ? "Unable to create account." : "Invalid username or password."));
      }
      const { access_token: accessToken } = await response.json();
      window.sessionStorage.setItem("avip_access_token", accessToken);
      const meResponse = await fetch(`${apiRoot}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!meResponse.ok) throw new Error("Unable to load the signed-in user.");
      setCurrentUser(await meResponse.json());
      setPassword("");
      setEmail("");
    } catch (signInError) {
      setAuthError(signInError instanceof Error ? signInError.message : "Unable to sign in.");
    } finally {
      setIsSigningIn(false);
    }
  }

  function signOut() {
    window.sessionStorage.removeItem("avip_access_token");
    setCurrentUser(null);
  }

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

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          {currentUser ? (
            <div className="flex flex-wrap items-center justify-between gap-4">
              <p className="text-sm text-slate-300">
                Signed in as <span className="font-semibold text-cyan-300">{currentUser.username}</span>
              </p>
              <button
                type="button"
                onClick={signOut}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
              >
                Sign out
              </button>
            </div>
          ) : (
            <form onSubmit={submitAuth} className="grid gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
              <label className="text-sm text-slate-300">
                Username
                <input
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
                  required
                />
              </label>
              {authMode === "register" ? (
                <label className="text-sm text-slate-300">
                  Email
                  <input
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
                    required
                  />
                </label>
              ) : null}
              <label className="text-sm text-slate-300">
                Password
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
                  minLength={authMode === "register" ? 12 : undefined}
                  required
                />
              </label>
              <button
                type="submit"
                disabled={isSigningIn}
                className="rounded-lg bg-cyan-500 px-4 py-2 font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSigningIn ? "Please wait..." : authMode === "register" ? "Create account" : "Sign in"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setAuthMode(authMode === "login" ? "register" : "login");
                  setAuthError(null);
                }}
                className="text-left text-sm text-cyan-300 hover:text-cyan-200 sm:col-span-3"
              >
                {authMode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
              </button>
              {authError ? <p className="text-sm text-amber-300 sm:col-span-3">{authError}</p> : null}
            </form>
          )}
        </section>

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
