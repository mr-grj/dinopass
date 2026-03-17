const KEY = "keyDerivation";

const STRENGTH_LEVELS = [
  { label: "Very Weak", color: "#d32f2f", recommend: true },
  { label: "Weak", color: "#e65100", recommend: true },
  { label: "Fair", color: "#f9a825", recommend: true },
  { label: "Strong", color: "#2e7d32", recommend: false },
  { label: "Very Strong", color: "#1b5e20", recommend: false },
];

export const getPasswordStrength = (password) => {
  if (!password) return null;

  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (password.length >= 16) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  // Short passwords are capped
  if (password.length < 6) score = Math.min(score, 0);
  else if (password.length < 8) score = Math.min(score, 1);

  const level = Math.min(Math.max(Math.floor((score / 6) * 5), 0), 4);
  return { level, ...STRENGTH_LEVELS[level] };
};

export const formatDuration = (ms) => {
  const secs = Math.round(ms / 1000);
  if (secs >= 60 && secs % 60 === 0) {
    const mins = secs / 60;
    return `${mins} minute${mins !== 1 ? "s" : ""}`;
  }
  return `${secs} second${secs !== 1 ? "s" : ""}`;
};

export const setKeyDerivation = (value) => {
  if (!value) return;
  sessionStorage.setItem(KEY, value);
};

export const isAuth = () => !!sessionStorage.getItem(KEY);
export const getKeyDerivation = () => sessionStorage.getItem(KEY);
export const removeKeyDerivation = () => sessionStorage.removeItem(KEY);
