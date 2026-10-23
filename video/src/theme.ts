import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont("normal", { weights: ["400", "600", "800"], subsets: ["latin"] });

export const FONT = fontFamily;
export const BG = "#0e1014";
export const PANEL = "#181b21";
export const INK = "#f4f3ef";
export const INK_2 = "#b9b8b1";
export const MUTED = "#7d7c76";
export const ACCENT = "#3987e5";
export const WARN = "#e66767";

// Reference categorical palette, dark-mode steps, fixed order.
export const SERIES: Record<string, string> = {
  haiku: "#3987e5",
  sonnet: "#d95926",
  opus: "#199e70",
  gpt: "#c98500",
  gemini: "#d55181",
};
