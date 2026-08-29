/**
 * Feature 55 — Transaction Reference.
 *
 * Generates a mock, display-only transaction reference such as
 * `TX-DEMO-A1B2C3`. This is NOT a real transaction identifier and has no
 * backing persistence — it exists purely so success/receipt screens have
 * something reference-shaped to show during the demo. A real backend
 * would issue its own authoritative reference (or the actual transaction
 * ID) at transfer-creation time; this helper should be deleted once that
 * exists, and any UI using it should switch to the server-provided value.
 */
const REFERENCE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const REFERENCE_LENGTH = 6;

export function generateMockTransactionReference(): string {
  let suffix = '';
  for (let i = 0; i < REFERENCE_LENGTH; i += 1) {
    suffix += REFERENCE_CHARS.charAt(Math.floor(Math.random() * REFERENCE_CHARS.length));
  }
  return `TX-DEMO-${suffix}`;
}
