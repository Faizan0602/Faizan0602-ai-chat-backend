import { useState } from "react";
import api from "../api";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await api.post("/auth/register", { email, password });
      navigate("/login");
    } catch (error) {
      setError(error.response?.data?.detail || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f7f8fb] px-4 py-10">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/60">
        <div className="mb-8">
          <p className="mb-3 font-['Space_Grotesk'] text-sm font-bold uppercase tracking-[0.18em] text-indigo-600">Orbit</p>
          <h1 className="font-['Space_Grotesk'] text-3xl font-bold tracking-tight text-slate-900">Create your account</h1>
          <p className="mt-2 text-sm text-slate-500">A calmer place to think with AI.</p>
        </div>
        <form onSubmit={handleRegister} className="space-y-5">
          {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          <label className="block text-sm font-semibold text-slate-700">
            Email
            <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="you@example.com" />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Password
            <input required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} type="password" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="At least 6 characters" />
          </label>
          <button disabled={isLoading} type="submit" className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">{isLoading ? "Creating account..." : "Create account"}</button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">Already have an account? <Link className="font-semibold text-indigo-600 hover:text-indigo-700" to="/login">Sign in</Link></p>
      </section>
    </main>
  );
}