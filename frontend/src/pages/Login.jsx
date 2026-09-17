import { useState } from "react";
import api from "../api";
import { Link, useNavigate } from "react-router-dom";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || fallback;

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);

      const res = await api.post("/auth/login", form, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      navigate("/chat");
    } catch (error) {
      setError(getErrorMessage(error, "Invalid email or password"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f7f8fb] px-4 py-10">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/60">
        <div className="mb-8">
          <p className="mb-3 font-['Space_Grotesk'] text-sm font-bold uppercase tracking-[0.18em] text-indigo-600">Orbit</p>
          <h1 className="font-['Space_Grotesk'] text-3xl font-bold tracking-tight text-slate-900">Welcome back</h1>
          <p className="mt-2 text-sm text-slate-500">Sign in to continue your conversations.</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-5">
          {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          <label className="block text-sm font-semibold text-slate-700">
            Email
            <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="you@example.com" />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Password
            <input required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} type="password" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="Your password" />
          </label>
          <button disabled={isLoading} type="submit" className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">{isLoading ? "Signing in..." : "Sign in"}</button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">New to Orbit? <Link className="font-semibold text-indigo-600 hover:text-indigo-700" to="/register">Create an account</Link></p>
      </section>
    </main>
  );
}