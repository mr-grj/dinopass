// Local, offline vault health analysis. Runs entirely on the already-decrypted
// rows the vault holds in memory, so it never sends anything anywhere (no
// breach-check API, no third party). Flags the three things individual users
// actually care about: weak, reused, and stale passwords.

import { getPasswordStrength } from "./passwordStrength";

const STALE_DAYS = 365;

const ageInDays = (updated) =>
  updated ? (Date.now() - new Date(updated).getTime()) / 86_400_000 : 0;

export const analyzeVault = (passwords) => {
  const logins = passwords.filter((entry) => entry.kind !== "note");
  const weak = [];
  const stale = [];
  const byValue = new Map();

  for (const entry of logins) {
    const strength = getPasswordStrength(entry.password_value);
    if (strength && strength.level <= 2) weak.push(entry);

    if (ageInDays(entry.updated) > STALE_DAYS) stale.push(entry);

    const bucket = byValue.get(entry.password_value) ?? [];
    bucket.push(entry);
    byValue.set(entry.password_value, bucket);
  }

  const reused = [];
  for (const bucket of byValue.values()) {
    if (bucket.length > 1) reused.push(...bucket);
  }

  const flagged = new Set([...weak, ...reused, ...stale].map((entry) => entry.password_name));
  const score =
    logins.length === 0 ? 100 : Math.round(((logins.length - flagged.size) / logins.length) * 100);

  return { weak, reused, stale, score, total: logins.length };
};
