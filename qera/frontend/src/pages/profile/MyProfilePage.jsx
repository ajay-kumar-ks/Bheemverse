import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";

function Avatar({ profile }) {
  const initials = profile?.name
    ?.split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  if (profile?.avatar_url) {
    return <img src={profile.avatar_url} alt="" className="h-20 w-20 rounded-full border border-slate-200 object-cover" />;
  }
  return (
    <div className="flex h-20 w-20 items-center justify-center rounded-full bg-indigo-100 text-xl font-bold text-indigo-700">
      {initials || "U"}
    </div>
  );
}

export default function MyProfilePage() {
  const { refreshUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [topicInput, setTopicInput] = useState("");
  const [form, setForm] = useState({
    name: "",
    avatar_url: "",
    bio: "",
    preferred_topics: [],
    learning_goals: "",
    notification_preferences: { email: true, in_app: true, exam_reminders: true },
  });
  const [badges, setBadges] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    async function loadProfile() {
      setLoading(true);
      try {
        const response = await api.get("/users/me");
        const data = response.data;
        setProfile(data);
        setForm({
          name: data.name || "",
          avatar_url: data.avatar_url || "",
          bio: data.bio || "",
          preferred_topics: data.preferred_topics || [],
          learning_goals: data.learning_goals || "",
          notification_preferences: {
            email: data.notification_preferences?.email ?? true,
            in_app: data.notification_preferences?.in_app ?? true,
            exam_reminders: data.notification_preferences?.exam_reminders ?? true,
          },
        });

        const badgesResponse = await api.get("/users/me/badges");
        setBadges(badgesResponse.data || []);
      } catch {
        setError("Unable to load profile.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  const addTopic = () => {
    const value = topicInput.trim().toLowerCase();
    if (!value || form.preferred_topics.includes(value)) return;
    setForm((prev) => ({ ...prev, preferred_topics: [...prev.preferred_topics, value] }));
    setTopicInput("");
  };

  const removeTopic = (topic) => {
    setForm((prev) => ({ ...prev, preferred_topics: prev.preferred_topics.filter((item) => item !== topic) }));
  };

  async function saveChanges(event) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      const response = await api.put("/users/me", form);
      setProfile(response.data);
      await refreshUser();
      setEditing(false);
      setSuccess("Profile settings updated.");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to save profile.");
    }
  }

  if (loading) {
    return <div className="mx-auto max-w-5xl px-4 py-8 text-sm text-slate-500">Loading profile...</div>;
  }

  if (error && !profile) {
    return <div className="mx-auto max-w-5xl px-4 py-8 text-sm text-rose-600">{error}</div>;
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex flex-col gap-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <Avatar profile={profile} />
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{profile?.name}</h1>
            <p className="text-sm text-slate-600">{profile?.email}</p>
            <p className="mt-2 max-w-2xl text-sm text-slate-700">{profile?.bio || "No bio added yet."}</p>
          </div>
        </div>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
          onClick={() => setEditing((current) => !current)}
        >
          {editing ? "Cancel" : "Edit settings"}
        </button>
      </div>

      {success && <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{success}</div>}
      {error && <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</div>}

      {editing && (
        <form className="mb-8 space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" onSubmit={saveChanges}>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-slate-700" htmlFor="profile-name">Name</label>
              <input
                id="profile-name"
                className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                value={form.name}
                onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700" htmlFor="profile-avatar">Profile picture URL</label>
              <input
                id="profile-avatar"
                className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                value={form.avatar_url}
                onChange={(event) => setForm((prev) => ({ ...prev, avatar_url: event.target.value }))}
                placeholder="https://..."
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="profile-bio">Bio</label>
            <textarea
              id="profile-bio"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              rows={4}
              value={form.bio}
              onChange={(event) => setForm((prev) => ({ ...prev, bio: event.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="profile-goals">Learning goals</label>
            <textarea
              id="profile-goals"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              rows={3}
              value={form.learning_goals}
              onChange={(event) => setForm((prev) => ({ ...prev, learning_goals: event.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="profile-topic">Preferred topics</label>
            <div className="mt-1 flex flex-col gap-2 sm:flex-row">
              <input
                id="profile-topic"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                value={topicInput}
                onChange={(event) => setTopicInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addTopic();
                  }
                }}
              />
              <button type="button" onClick={addTopic} className="rounded-lg bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200">
                Add topic
              </button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {form.preferred_topics.map((topic) => (
                <button key={topic} type="button" onClick={() => removeTopic(topic)} className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                  #{topic} x
                </button>
              ))}
            </div>
          </div>

          <fieldset className="rounded-xl border border-slate-200 p-4">
            <legend className="px-1 text-sm font-semibold text-slate-700">Notification preferences</legend>
            <div className="mt-3 grid gap-3 sm:grid-cols-3">
              {[
                ["email", "Email"],
                ["in_app", "In-app"],
                ["exam_reminders", "Exam reminders"],
              ].map(([key, label]) => (
                <label key={key} className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={Boolean(form.notification_preferences[key])}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        notification_preferences: { ...prev.notification_preferences, [key]: event.target.checked },
                      }))
                    }
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>

          <button type="submit" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-300">
            Save settings
          </button>
        </form>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Stats</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            <div>Global Rank: {profile.stats.global_rank ?? "N/A"}</div>
            <div>Exams Attended: {profile.stats.exams_attended}</div>
            <div>Exams Created: {profile.stats.exams_created}</div>
            <div>Questions Created: {profile.stats.questions_created}</div>
            <div>Accuracy: {profile.stats.accuracy?.toFixed(1)}%</div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Achievements</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            {badges.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {badges.map((badge) => (
                  <div
                    key={badge.id}
                    className="group relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-950/5 via-white to-slate-50 p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
                  >
                    <div className="absolute right-4 top-4 h-12 w-12 rounded-full bg-slate-900/5 blur-xl opacity-80" />
                    <div className="relative flex items-center gap-4">
                      <div className="flex h-16 w-16 items-center justify-center rounded-full border border-slate-200 bg-white text-2xl text-indigo-700 shadow-sm">
                        {badge.icon_url ? (
                          <img src={badge.icon_url} alt={badge.name} className="h-12 w-12 rounded-full object-cover" />
                        ) : (
                          badge.name.charAt(0).toUpperCase()
                        )}
                      </div>
                      <div className="min-w-0">
                        <div className="truncate text-sm font-semibold text-slate-900">{badge.name}</div>
                        <div className="mt-1 truncate text-xs text-slate-500">{badge.description}</div>
                        {badge.unlocked_at ? (
                          <div className="mt-2 text-[11px] uppercase tracking-wide text-slate-400">Unlocked {new Date(badge.unlocked_at).toLocaleDateString()}</div>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-500">No badges earned yet. Take exams and engage with the app to unlock achievements.</div>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
          <h2 className="text-lg font-semibold">Learning profile</h2>
          <p className="mt-3 text-sm text-slate-700">{profile.learning_goals || "No learning goals added yet."}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {(profile.preferred_topics || []).length ? profile.preferred_topics.map((topic) => (
              <span key={topic} className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">#{topic}</span>
            )) : <span className="text-sm text-slate-500">No preferred topics yet.</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
