import { ref } from "vue";

type Theme = "dark" | "light";
const KEY = "app-theme";

function initial(): Theme {
  try {
    const t = localStorage.getItem(KEY);
    if (t === "light" || t === "dark") return t;
  } catch {
    /* ignore */
  }
  return "dark"; // dark by default
}

export const theme = ref<Theme>(initial());
document.documentElement.dataset.theme = theme.value;

export function toggleTheme() {
  theme.value = theme.value === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = theme.value;
  try {
    localStorage.setItem(KEY, theme.value);
  } catch {
    /* ignore */
  }
}
