/**
 * Utility helper for conditionally combining class names.
 */
export function cn(...inputs) {
  return inputs.flat().filter(Boolean).join(" ");
}

export default cn;
