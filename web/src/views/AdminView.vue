<script setup lang="ts">
// Moderation (new in v2): flagged reports, hidden reports, users.
import { onMounted, ref, watch } from "vue";
import ReportCard from "../components/ReportCard.vue";
import { get, post } from "../lib/api";
import { t } from "../lib/i18n";
import type { Me, Paged, Report } from "../lib/types";

const tab = ref<"flags" | "hidden" | "users">("flags");
const flags = ref<{ report: Report; flags: number; reasons: string[] }[]>([]);
const hidden = ref<Report[]>([]);
const users = ref<Me[]>([]);
const q = ref("");

async function load() {
  if (tab.value === "flags") flags.value = (await get<Paged<{ report: Report; flags: number; reasons: string[] }>>("/api/admin/flags")).items;
  if (tab.value === "hidden") hidden.value = (await get<Paged<Report>>("/api/reports", { status: "hidden", per_page: 50 })).items;
  if (tab.value === "users") users.value = (await get<Paged<Me>>("/api/admin/users", { q: q.value, per_page: 50 })).items;
}

async function hide(r: Report) {
  const reason = prompt(t("admin.hideReason"));
  if (!reason) return;
  await post(`/api/admin/reports/${r.id}/hide`, { reason });
  load();
}
const restore = async (r: Report) => { await post(`/api/admin/reports/${r.id}/restore`); load(); };
const dismiss = async (r: Report) => { await post(`/api/admin/reports/${r.id}/dismiss-flags`); load(); };
const setBlocked = async (u: Me, block: boolean) => { await post(`/api/admin/users/${u.id}/${block ? "block" : "unblock"}`); load(); };

watch(tab, load);
onMounted(load);
</script>

<template>
  <h1>{{ t("admin.title") }}</h1>
  <div class="segmented tabs">
    <button :class="{ on: tab === 'flags' }" @click="tab = 'flags'">{{ t("admin.flags") }}</button>
    <button :class="{ on: tab === 'hidden' }" @click="tab = 'hidden'">{{ t("admin.hidden") }}</button>
    <button :class="{ on: tab === 'users' }" @click="tab = 'users'">{{ t("admin.users") }}</button>
  </div>

  <section v-if="tab === 'flags'" class="grid">
    <div v-for="f in flags" :key="f.report.id" class="stack">
      <ReportCard :report="f.report" />
      <div class="row small">
        <span class="chip hidden">{{ t("admin.flagsCount", { n: f.flags }) }}</span>
        <span v-for="r in f.reasons" :key="r" class="chip">{{ t(`flag.${r}` as "flag.fake") }}</span>
      </div>
      <div class="row">
        <button v-if="f.report.status !== 'hidden'" class="btn sm danger" @click="hide(f.report)">{{ t("admin.hide") }}</button>
        <button v-else class="btn sm" @click="restore(f.report)">{{ t("admin.restore") }}</button>
        <button class="btn sm ghost" @click="dismiss(f.report)">{{ t("admin.dismiss") }}</button>
      </div>
    </div>
    <p v-if="!flags.length" class="empty">{{ t("admin.empty") }}</p>
  </section>

  <section v-if="tab === 'hidden'" class="grid">
    <div v-for="r in hidden" :key="r.id" class="stack">
      <ReportCard :report="r" />
      <p class="muted small">{{ r.hidden_reason }}</p>
      <button class="btn sm" @click="restore(r)">{{ t("admin.restore") }}</button>
    </div>
    <p v-if="!hidden.length" class="empty">{{ t("admin.empty") }}</p>
  </section>

  <section v-if="tab === 'users'" class="stack">
    <form class="row" @submit.prevent="load"><input v-model="q" class="input" :placeholder="t('filter.search')" /></form>
    <div class="card">
      <div v-for="u in users" :key="u.id" class="user row spread">
        <div class="row">
          <img v-if="u.avatar_url" :src="u.avatar_url" class="avatar" alt="" />
          <div><strong>{{ u.name }}</strong><div class="muted small" dir="ltr">{{ u.email }}</div></div>
          <span v-if="u.role === 'admin'" class="chip resolved">admin</span>
          <span v-if="!u.is_active" class="chip hidden">{{ t("admin.blocked") }}</span>
        </div>
        <button v-if="u.role !== 'admin'" class="btn sm" :class="{ danger: u.is_active }" @click="setBlocked(u, u.is_active)">
          {{ u.is_active ? t("admin.block") : t("admin.unblock") }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.tabs { margin-block-end: 18px; }
.user { padding: 12px 16px; border-block-end: 1px solid var(--border); }
</style>
