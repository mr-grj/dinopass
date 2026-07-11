import apiClient from "../api/client";

export const GITHUB_REPO = import.meta.env.VITE_GITHUB_REPO || "mr-grj/ciphermoth";

const RELEASE_API = `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`;

const parseVersion = (value) =>
  String(value ?? "")
    .trim()
    .replace(/^v/i, "")
    .split(".")
    .map((part) => parseInt(part, 10) || 0);

export const compareVersions = (a, b) => {
  const pa = parseVersion(a);
  const pb = parseVersion(b);
  const len = Math.max(pa.length, pb.length);
  for (let i = 0; i < len; i += 1) {
    const diff = (pa[i] || 0) - (pb[i] || 0);
    if (diff !== 0) return diff > 0 ? 1 : -1;
  }
  return 0;
};

const fetchCurrentVersion = async () => {
  const { data } = await apiClient.get("/meta");
  return data.version;
};

const fetchLatestRelease = async () => {
  const resp = await fetch(RELEASE_API, {
    headers: { Accept: "application/vnd.github+json" },
  });
  if (!resp.ok) throw new Error(`GitHub responded ${resp.status}`);
  const data = await resp.json();
  return { tag: data.tag_name, releaseUrl: data.html_url };
};

export const getUpdateStatus = async () => {
  try {
    const [current, release] = await Promise.all([fetchCurrentVersion(), fetchLatestRelease()]);
    if (!current || !release?.tag) return null;
    return {
      current,
      latest: release.tag,
      releaseUrl: release.releaseUrl,
      updateAvailable: compareVersions(release.tag, current) > 0,
    };
  } catch {
    return null;
  }
};
