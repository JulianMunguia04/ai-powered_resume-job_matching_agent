
const STORAGE_KEY = "matchpilot_recent_activity";
const ACTIVITY_EVENT = "recent-activity-updated";
const EXPIRATION_TIME = 5 * 60 * 1000; // 5 minutes
const MAX_ACTIVITIES = 8;

export function getRecentActivity() {
  if (typeof window === "undefined") return [];

  try {
    const saved = JSON.parse(
      localStorage.getItem(STORAGE_KEY) || "[]"
    );

    const now = Date.now();

    const validActivities = saved.filter(
      (item) =>
        item &&
        item.id &&
        item.type &&
        item.createdAt &&
        now - item.createdAt < EXPIRATION_TIME
    );

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(validActivities)
    );

    return validActivities;
  } catch (error) {
    console.error("Unable to read recent activity:", error);
    return [];
  }
}

export function recordRecentActivity({ type, id, title }) {
  if (typeof window === "undefined") return;

  if (!["resume", "job"].includes(type) || !id) return;

  try {
    const existing = getRecentActivity();

    const activity = {
      type,
      id: String(id),
      title: title || (type === "resume" ? "Uploaded resume" : "New job"),
      createdAt: Date.now(),
    };

    // Remove an older entry for the same document.
    const updated = [
      activity,
      ...existing.filter(
        (item) =>
          !(item.type === type && String(item.id) === String(id))
      ),
    ].slice(0, MAX_ACTIVITIES);

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(updated)
    );

    window.dispatchEvent(
      new Event(ACTIVITY_EVENT)
    );
  } catch (error) {
    console.error("Unable to save recent activity:", error);
  }
}

export { ACTIVITY_EVENT };
