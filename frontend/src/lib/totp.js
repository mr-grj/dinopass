// Time-based one-time password (RFC 6238, HMAC-SHA1) computed with the Web
// Crypto API. React-free and isolated, like passwordGenerator.js, so the
// two-factor path is easy to audit. The backend has a matching stdlib version
// for the CLI; nothing here ever leaves the browser.

const BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
const DEFAULT_PERIOD = 30;
const DEFAULT_DIGITS = 6;

const base32Decode = (secret) => {
  const clean = secret.replace(/=+$/, "").replace(/\s/g, "").toUpperCase();
  const bytes = [];
  let bits = 0;
  let value = 0;

  for (const char of clean) {
    const index = BASE32_ALPHABET.indexOf(char);
    if (index === -1) throw new Error("Invalid base32 secret.");
    value = (value << 5) | index;
    bits += 5;
    if (bits >= 8) {
      bits -= 8;
      bytes.push((value >>> bits) & 0xff);
    }
  }

  return new Uint8Array(bytes);
};

// Seconds until the current code rolls over. Drives the countdown ring.
export const totpRemaining = (period = DEFAULT_PERIOD) =>
  period - (Math.floor(Date.now() / 1000) % period);

export const generateTotp = async (
  secret,
  { digits = DEFAULT_DIGITS, period = DEFAULT_PERIOD } = {}
) => {
  const key = base32Decode(secret);

  // 8-byte big-endian counter, built without BigInt to stay simple.
  const message = new Uint8Array(8);
  let counter = Math.floor(Date.now() / 1000 / period);
  for (let i = 7; i >= 0; i -= 1) {
    message[i] = counter & 0xff;
    counter = Math.floor(counter / 256);
  }

  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    key,
    { name: "HMAC", hash: "SHA-1" },
    false,
    ["sign"]
  );
  const signature = new Uint8Array(await crypto.subtle.sign("HMAC", cryptoKey, message));

  const offset = signature[signature.length - 1] & 0x0f;
  const binary =
    ((signature[offset] & 0x7f) << 24) |
    (signature[offset + 1] << 16) |
    (signature[offset + 2] << 8) |
    signature[offset + 3];

  return String(binary % 10 ** digits).padStart(digits, "0");
};
