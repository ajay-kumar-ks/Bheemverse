import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";

export default function MyProfilePage() {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ name: "", avatar_url: "", bio: "" });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const response = await api.get("/users/me");
        setProfile(response.data);
        setForm({ name: response.data.name || "", avatar_url: response.data.avatar_url || "", bio: response.data.bio || "" });
      } catch (err) {
        setError("Unable to load profile.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  async function saveChanges(event) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      const response = await api.put("/users/me", form);
      setProfile(response.data);
      await refreshUser();
      setEditing(false);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError("Unable to save profile.");
    }
  }

  if (loading) {
    return <div className="p-8">Loading profile...</div>;
  }

  if (error && !profile) {
    return <div className="p-8 text-red-500">{error}</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6 flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">{profile?.name}</h1>
          <p className="text-sm text-gray-600">{profile?.email}</p>
          <p className="mt-3 text-gray-700">{profile?.bio || "No bio added yet."}</p>
        </div>
        <button
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          onClick={() => setEditing((current) => !current)}
        >
          {editing ? "Cancel" : "Edit Profile"}
        </button>
      </div>

      {success && <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{success}</div>}
      {error && <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</div>}

      {editing && (
        <form className="mb-8 space-y-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm" onSubmit={saveChanges}>
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <input
              className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none"
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Avatar URL</label>
            <input
              className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none"
              value={form.avatar_url}
              onChange={(event) => setForm((prev) => ({ ...prev, avatar_url: event.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Bio</label>
            <textarea
              className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none"
              rows={4}
              value={form.bio}
              onChange={(event) => setForm((prev) => ({ ...prev, bio: event.target.value }))}
            />
          </div>
          <button type="submit" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700">
            Save Changes
          </button>
        </form>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-3">Stats</h2>
          <div className="space-y-3 text-sm text-gray-700">
            <div>Global Rank: {profile.stats.global_rank ?? "N/A"}</div>
            <div>Exams Attended: {profile.stats.exams_attended}</div>
            <div>Exams Created: {profile.stats.exams_created}</div>
            <div>Questions Created: {profile.stats.questions_created}</div>
            <div>Accuracy: {profile.stats.accuracy?.toFixed(1)}%</div>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm lg:col-span-2">
          <h2 className="text-lg font-semibold mb-3">Recent Activity</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">Recent Questions</h3>
              {profile.recent_questions.length === 0 ? (
                <p className="text-sm text-gray-500">No recent questions.</p>
              ) : (
                <ul className="mt-3 space-y-2 text-sm text-gray-700">
                  {profile.recent_questions.map((question) => (
                    <li key={question.id} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                      <div className="font-medium">{question.title}</div>
                      <div className="text-xs text-gray-500">Difficulty: {question.difficulty}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <h3 className="font-medium">Recent Exams</h3>
              {profile.recent_exams.length === 0 ? (
                <p className="text-sm text-gray-500">No recent exams.</p>
              ) : (
                <ul className="mt-3 space-y-2 text-sm text-gray-700">
                  {profile.recent_exams.map((exam) => (
                    <li key={exam.id} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                      <div className="font-medium">{exam.title}</div>
                      <div className="text-xs text-gray-500">Marks: {exam.total_marks} • Duration: {exam.duration_minutes} mins</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
