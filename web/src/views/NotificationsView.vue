<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { get, post } from "../lib/api";
import { t, timeAgo } from "../lib/i18n";
import type { AppNotification } from "../lib/types";

const router = useRouter();
const items = ref<AppNotification[] | null>(null);

async function load() {
  items.value = (await get<{ items: AppNotification[] }>("/api/notifications", { per_page: 50 })).items;
}

function text(n: AppNotification): string {
  return t(`notif.${n.type}`, { actor: n.actor?.name ?? "", score: Math.round(Number(n.data.score ?? 0)) });
}

async function open(n: AppNotification) {
  if (!n.read) await post(`/api/notifications/${n.id}/read`);
  router.push(n.link);
}

async function readAll() {
  await post("/api/notifications/read-all");
  load();
}

onMounted(load);
</script>

<template>
  <div class="row spread">
    <h1>{{ t("notifications.title") }}</h1>
    <button class="btn sm" @click="readAll">{{ t("notifications.readAll") }}</button>
  </div>
  <p v-if="items === null" class="empty">{{ t("common.loading") }}</p>
  <p v-else-if="!items.length" class="empty">{{ t("notifications.empty") }}</p>
  <div v-else class="card list">
    <button v-for="n in items" :key="n.id" class="item" :class="{ unread: !n.read }" @click="open(n)">
      <span class="icon">{{ { comment: "💬", like: "♥", message: "✉", match: "🔎", match_confirmed: "✅" }[n.type] }}</span>
      <img v-if="n.actor?.avatar_url" :src="n.actor.avatar_url" class="avatar" alt="" />
      <span class="grow">
        <strong>{{ text(n) }}</strong>
        <span v-if="n.data.preview" class="muted small preview">“{{ n.data.preview }}”</span>
      </span>
      <span class="muted small">{{ timeAgo(n.created_at) }}</span>
    </button>
  </div>
</template>

<style scoped>
.list { overflow: hidden; }
.item { display: flex; gap: 12px; align-items: center; inline-size: 100%; padding: 14px 16px; background: none; border: 0; border-block-end: 1px solid var(--border); cursor: pointer; text-align: start; }
.item:hover { background: var(--surface-2); }
.item.unread { background: var(--primary-soft); }
.icon { font-size: 18px; inline-size: 24px; text-align: center; }
.grow { flex: 1; display: grid; }
.preview { display: block; }
</style>
