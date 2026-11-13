import { reactive } from "vue";
import type { Me } from "./types";

const KEY = "app-session";

function load(): { token: string | null; user: Me | null } {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* private mode */
  }
  return { token: null, user: null };
}

const initial = load();

export const session = reactive({
  token: initial.token as string | null,
  user: initial.user as Me | null,
  set(token: string, user: Me) {
    this.token = token;
    this.user = user;
    this.persist();
  },
  setUser(user: Me) {
    this.user = user;
    this.persist();
  },
  clear() {
    this.token = null;
    this.user = null;
    this.persist();
  },
  persist() {
    try {
      localStorage.setItem(KEY, JSON.stringify({ token: this.token, user: this.user }));
    } catch {
      /* ignore */
    }
  },
  get isAdmin() {
    return this.user?.role === "admin";
  },
});
