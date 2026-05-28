import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../services/api";

export default function PublicProfilePage() {
  const { uid } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const response = await api.get(`/users/${uid}`);
        setProfile(response.data);
      } catch (err) {
        setError("Unable to load profile.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, [uid]);

  if (loading) {
    return <div className="p-8">Loading profile...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-500">{error}</div>;
  }

  if (!profile) {
    return <div className="p-8 text-gray-600">Profile not found.</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-3xl font-bold">{profile.name}</h1>
        <p className="text-sm text-gray-600">{profile.email}</p>
        <p className="mt-3 text-gray-700">{profile.bio || "No bio available."}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
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

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm md:col-span-2">
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
