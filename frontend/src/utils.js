const KEY = "keyDerivation";

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
