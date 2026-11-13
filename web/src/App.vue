<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";
import { get, post } from "./lib/api";
import { locale, t, toggleLocale } from "./lib/i18n";
import { session } from "./lib/session";
import { theme, toggleTheme } from "./lib/theme";
import type { Me } from "./lib/types";

const router = useRouter();
const unread = ref(0);
const unreadMessages = ref(0);
const menuOpen = ref(false);
let timer: number | undefined;

async function refreshCounts() {
  if (!session.token) return;
  try {
    unread.value = (await get<{ unread: number }>("/api/notifications/unread-count")).unread;
    unreadMessages.value = (await get<{ unread: number }>("/api/messages/unread-count")).unread;
  } catch {
    /* offline or logged out */
  }
}

async function refreshMe() {
  if (!session.token) return;
  try {
    session.setUser(await get<Me>("/api/auth/me"));
  } catch {
    /* token no longer valid: api() cleared it */
  }
}

async function logout() {
  try {
    await post("/api/auth/logout");
  } catch {
    /* already logged out */
  }
  session.clear();
  router.push("/");
}

onMounted(() => {
  refreshMe();
  refreshCounts();
  // v1 used Pusher broadcasting; v2 polls the counters (no third-party realtime account needed)
  timer = window.setInterval(refreshCounts, 20000);
});
onBeforeUnmount(() => window.clearInterval(timer));
watch(() => session.token, refreshCounts);
watch(() => router.currentRoute.value.fullPath, () => { menuOpen.value = false; refreshCounts(); });
</script>

<template>
  <div :key="locale">
    <header class="topbar">
      <div class="container row spread">
        <RouterLink to="/" class="brand">
          <span class="logo" aria-hidden="true">
            <svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" /><circle cx="16" cy="12" r="5" class="w" /><path d="M7 26c1.5-5 5-7 9-7s7.5 2 9 7" class="w" /></svg>
          </span>
          <span>
            <strong>{{ t("app.name") }}</strong>
            <small class="muted hide-sm">{{ t("app.tagline") }}</small>
          </span>
        </RouterLink>

        <button class="btn ghost sm menu-btn" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-label="menu">☰</button>

        <nav class="nav" :class="{ open: menuOpen }">
          <RouterLink to="/">{{ t("nav.home") }}</RouterLink>
          <template v-if="session.token">
            <RouterLink to="/matches">{{ t("nav.matches") }}</RouterLink>
            <RouterLink to="/messages">{{ t("nav.messages") }} <span v-if="unreadMessages" class="badge">{{ unreadMessages }}</span></RouterLink>
            <RouterLink to="/notifications">{{ t("nav.notifications") }} <span v-if="unread" class="badge">{{ unread }}</span></RouterLink>
            <RouterLink v-if="session.isAdmin" to="/admin">{{ t("nav.admin") }}</RouterLink>
          </template>
          <span class="sep" />
          <button class="btn ghost sm" @click="toggleLocale">{{ t("toggle.lang") }}</button>
          <button class="btn ghost sm" @click="toggleTheme" :aria-label="t(theme === 'dark' ? 'toggle.theme.dark' : 'toggle.theme.light')">
            {{ theme === "dark" ? "☀" : "☾" }}
          </button>
          <template v-if="session.token && session.user">
            <RouterLink to="/reports/new" class="btn primary sm">+ {{ t("nav.new") }}</RouterLink>
            <RouterLink to="/me" class="me">
              <img v-if="session.user.avatar_url" :src="session.user.avatar_url" class="avatar" alt="" />
              <span class="hide-sm">{{ session.user.name }}</span>
            </RouterLink>
            <button class="btn ghost sm" @click="logout">{{ t("nav.logout") }}</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="btn sm">{{ t("nav.login") }}</RouterLink>
            <RouterLink to="/register" class="btn primary sm">{{ t("nav.register") }}</RouterLink>
          </template>
        </nav>
      </div>
    </header>

    <main class="container page">
      <RouterView />
    </main>

    <footer class="container footer muted small">
      <span>{{ t("app.name") }} · {{ t("app.tagline") }}</span>
      <span>{{ t("app.demo") }}</span>
    </footer>
  </div>
</template>

<style scoped>
.topbar {
  position: sticky; inset-block-start: 0; z-index: 20;
  background: color-mix(in srgb, var(--bg) 82%, transparent);
  backdrop-filter: blur(12px);
  border-block-end: 1px solid var(--border);
  padding-block: 10px;
}
.brand { display: flex; align-items: center; gap: 10px; color: var(--text); }
.brand:hover { text-decoration: none; }
.brand strong { display: block; font-size: 18px; }
.brand small { display: block; font-size: 12px; margin-block-start: -2px; }
.logo svg { inline-size: 36px; block-size: 36px; fill: var(--primary-strong); }
.logo .w { fill: #fff; }
.nav { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.nav > a:not(.btn) { padding-block: 6px; padding-inline: 10px; border-radius: 999px; color: var(--muted); font-weight: 600; display: inline-flex; gap: 6px; align-items: center; }
.nav > a.router-link-exact-active:not(.btn) { color: var(--text); background: var(--surface-2); }
.nav > a:hover { text-decoration: none; color: var(--text); }
.sep { inline-size: 1px; block-size: 22px; background: var(--border); margin-inline: 4px; }
.me { display: inline-flex; align-items: center; gap: 8px; color: var(--text); font-weight: 600; }
.menu-btn { display: none; }
.footer { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; padding-block: 24px; border-block-start: 1px solid var(--border); }
@media (max-width: 900px) {
  .menu-btn { display: inline-flex; }
  .nav { display: none; inline-size: 100%; padding-block-start: 10px; }
  .nav.open { display: flex; }
}
</style>
