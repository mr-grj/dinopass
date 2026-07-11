// Which stack is this build running on? React-free and tiny so it's easy to audit.
//
// The development stack serves the app through the Vite dev server, where
// `import.meta.env.DEV` is true. The production stack ships a static `vite build`,
// where it is false. That build-time signal maps exactly onto our two Compose
// projects (ciphermoth-dev vs ciphermoth), so nobody has to remember to set a flag.
// An explicit VITE_APP_ENV still wins, for anyone running a custom setup.
const explicit = import.meta.env.VITE_APP_ENV;

export const IS_DEV = explicit ? explicit === "development" : import.meta.env.DEV;

// Shared so the badge and the AppBar accent line agree on the dev colour.
export const DEV_ACCENT = "#e0982f";
