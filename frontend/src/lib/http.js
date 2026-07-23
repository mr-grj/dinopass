// Shared helpers for the easy-peasy model thunks. React-free so the HTTP
// error/download plumbing stays in one auditable place.

// Turn FastAPI's `detail` into a human-readable string. It is a string for our
// domain errors, but an array of {msg,...} objects for pydantic 422 validation
// errors (over-long fields, invalid TOTP, too many tags/custom fields). Without
// this, such an array stringifies to "[object Object]" in the UI.
const detailMessage = (detail, fallback) => {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const msgs = detail
      .map((e) => e?.msg)
      .filter((m) => typeof m === "string")
      .map((m) => m.replace(/^Value error,\s*/i, ""));
    return msgs.length ? msgs.join("; ") : fallback;
  }
  return fallback;
};

// Pull the API's `detail` message off an axios error, falling back to `fallback`.
// Handles both JSON responses and the Blob body returned by blob-typed requests
// (backup, attachment download), where the error payload arrives as a Blob.
export const errorDetail = async (err, fallback) => {
  const data = err.response?.data;
  if (data instanceof Blob) {
    try {
      return detailMessage(JSON.parse(await data.text()).detail, fallback);
    } catch {
      // Blob wasn't JSON; fall back to the generic message.
      return fallback;
    }
  }
  return detailMessage(data?.detail, fallback);
};

// Save a Blob to disk via a transient object URL and anchor click.
export const triggerDownload = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};
