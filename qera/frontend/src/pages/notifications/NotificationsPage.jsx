import { useEffect, useState } from "react";
import api from "../../services/api";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadNotifications = async () => {
    try {
      const response = await api.get("/users/me/notifications");
      setNotifications(response.data);
    } catch (err) {
      setError("Unable to load notifications.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const markRead = async (notificationId) => {
    try {
      await api.put(`/users/me/notifications/${notificationId}/read`);
      await loadNotifications();
    } catch {
      setError("Unable to update notification status.");
    }
  };

  const markAllRead = async () => {
    try {
      await api.put("/users/me/notifications/read-all");
      await loadNotifications();
    } catch {
      setError("Unable to mark all notifications as read.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-sm text-gray-600">Review recent updates and activity on your account.</p>
        </div>
        <button
          type="button"
          onClick={markAllRead}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          Mark All Read
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16">Loading notifications...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : notifications.length === 0 ? (
        <div className="text-gray-600">No new notifications.</div>
      ) : (
        <div className="space-y-4">
          {notifications.map((notification) => (
            <div key={notification.id} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium">{notification.message}</p>
                  <p className="mt-2 text-sm text-gray-500">{new Date(notification.created_at).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      notification.is_read ? 'bg-green-100 text-green-700' : 'bg-rose-100 text-rose-700'
                    }`}
                  >
                    {notification.is_read ? "Read" : "Unread"}
                  </span>
                  {!notification.is_read && (
                    <button
                      type="button"
                      onClick={() => markRead(notification.id)}
                      className="rounded-lg bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-900 hover:bg-slate-200"
                    >
                      Mark read
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
