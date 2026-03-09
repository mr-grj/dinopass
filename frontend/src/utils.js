const KEY = "keyDerivation";

export const setKeyDerivation = (value) => {
  if (!value) return;
  sessionStorage.setItem(KEY, value);
};

export const isAuth = () => !!sessionStorage.getItem(KEY);
export const getKeyDerivation = () => sessionStorage.getItem(KEY);
export const removeKeyDerivation = () => sessionStorage.removeItem(KEY);
