// Cryptographically secure password generation.
// Kept isolated (and free of React) so the security-critical randomness is easy
// to audit and reuse. Never swap crypto.getRandomValues for Math.random().

// Uniform random integer in [0, max) using rejection sampling to avoid modulo bias.
export const secureRandBelow = (max) => {
  const reject = 0x100000000 % max;
  let v;
  do {
    v = crypto.getRandomValues(new Uint32Array(1))[0];
  } while (v < reject);
  return v % max;
};

const CHAR_POOLS = {
  uppercase: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  lowercase: "abcdefghijklmnopqrstuvwxyz",
  numbers: "0123456789",
  symbols: "!@#$%^&*()-_=+[]{}|;:,.<>?",
};

export const generatePassword = ({ length, uppercase, lowercase, numbers, symbols }) => {
  const pools = [];
  if (uppercase) pools.push(CHAR_POOLS.uppercase);
  if (lowercase) pools.push(CHAR_POOLS.lowercase);
  if (numbers) pools.push(CHAR_POOLS.numbers);
  if (symbols) pools.push(CHAR_POOLS.symbols);
  if (!pools.length) pools.push(CHAR_POOLS.lowercase);

  const full = pools.join("");
  // Guarantee at least one character from every selected pool, then fill the rest.
  const chars = pools.map((p) => p[secureRandBelow(p.length)]);
  while (chars.length < length) chars.push(full[secureRandBelow(full.length)]);

  // Fisher-Yates shuffle so the guaranteed characters aren't stuck at the front.
  for (let i = chars.length - 1; i > 0; i--) {
    const j = secureRandBelow(i + 1);
    [chars[i], chars[j]] = [chars[j], chars[i]];
  }
  return chars.join("");
};
