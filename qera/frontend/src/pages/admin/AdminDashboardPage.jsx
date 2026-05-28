import { useEffect, useState } from "react";
import api from "../../services/api";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState({ users: 0, flaggedComments: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const usersResponse = await api.get("/admin/users");
        const commentsResponse = await api.get("/admin/comments/flagged");
        setStats({ users: usersResponse.data.length, flaggedComments: commentsResponse.data.length });
      } catch (err) {
        setError("Unable to load admin dashboard.");
      } finally {
        setLoading(false);
      }
    }

    loadStats();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      {loading ? (
        <div className="text-center py-16">Loading dashboard...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Total Users</h2>
            <p className="text-5xl font-bold text-indigo-700">{stats.users}</p>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Flagged Comments</h2>
            <p className="text-5xl font-bold text-rose-700">{stats.flaggedComments}</p>
          </div>
        </div>
      )}
    </div>
  );
}
