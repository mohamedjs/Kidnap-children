<script setup lang="ts">
// v1 HomeComponent: feed with type tabs and filters (type, gender, age range, text).
import { onMounted, reactive, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import ReportCard from "../components/ReportCard.vue";
import { get } from "../lib/api";
import { t } from "../lib/i18n";
import { session } from "../lib/session";
import type { Counts, Paged, Report } from "../lib/types";

const route = useRoute();
const router = useRouter();
const f = reactive({
  kind: (route.query.kind as string) ?? "",
  q: (route.query.q as string) ?? "",
  gender: (route.query.gender as string) ?? "",
  age_from: (route.query.age_from as string) ?? "",
  age_to: (route.query.age_to as string) ?? "",
  city: (route.query.city as string) ?? "",
});
const items = ref<Report[]>([]);
const counts = ref<Record<string, Counts>>({});
const total = ref(0);
const page = ref(1);
const loading = ref(false);
const stats = ref({ missing_open: 0, found_open: 0, resolved: 0 });

async function load(reset = true) {
  loading.value = true;
  if (reset) page.value = 1;
  try {
    const res = await get<Paged<Report>>("/api/reports", { ...f, page: page.value, per_page: 12 });
    items.value = reset ? res.items : [...items.value, ...res.items];
    total.value = res.total;
    if (res.items.length) {
      const c = await get<Record<string, Counts>>("/api/engagement", { report_ids: res.items.map((r) => r.id).join(",") });
      counts.value = { ...counts.value, ...c };
    }
  } finally {
    loading.value = false;
  }
}

function apply() {
  router.replace({ query: Object.fromEntries(Object.entries(f).filter(([, v]) => v)) });
  load();
}

function clear() {
  Object.assign(f, { q: "", gender: "", age_from: "", age_to: "", city: "" });
  apply();
}

function more() {
  page.value += 1;
  load(false);
}

watch(() => f.kind, apply);
onMounted(async () => {
  load();
  stats.value = await get("/api/reports/stats");
});
</script>

<template>
  <section class="hero">
    <div>
      <h1>{{ t("home.title") }}</h1>
      <p class="muted">{{ t("home.subtitle") }}</p>
      <RouterLink :to="session.token ? '/reports/new' : '/register'" class="btn primary">+ {{ t("nav.new") }}</RouterLink>
    </div>
    <div class="stats">
      <div class="stat missing"><strong>{{ stats.missing_open }}</strong><span>{{ t("stats.missing") }}</span></div>
      <div class="stat found"><strong>{{ stats.found_open }}</strong><span>{{ t("stats.found") }}</span></div>
      <div class="stat resolved"><strong>{{ stats.resolved }}</strong><span>{{ t("stats.resolved") }}</span></div>
    </div>
  </section>

  <section class="card pad filters">
    <div class="row spread">
      <div class="segmented" role="tablist">
        <button :class="{ on: f.kind === '' }" @click="f.kind = ''">{{ t("filter.all") }}</button>
        <button :class="{ on: f.kind === 'missing' }" @click="f.kind = 'missing'">{{ t("filter.missing") }}</button>
        <button :class="{ on: f.kind === 'found' }" @click="f.kind = 'found'">{{ t("filter.found") }}</button>
      </div>
      <span class="muted small">{{ total }}</span>
    </div>
    <form class="filter-grid" @submit.prevent="apply">
      <input v-model="f.q" class="input q" :placeholder="t('filter.search')" />
      <select v-model="f.gender" class="input" :aria-label="t('filter.gender')">
        <option value="">{{ t("filter.gender") }}: {{ t("filter.any") }}</option>
        <option value="male">{{ t("gender.male") }}</option>
        <option value="female">{{ t("gender.female") }}</option>
      </select>
      <input v-model="f.age_from" class="input" type="number" min="0" max="17" :placeholder="t('filter.ageFrom')" />
      <input v-model="f.age_to" class="input" type="number" min="0" max="17" :placeholder="t('filter.ageTo')" />
      <input v-model="f.city" class="input" :placeholder="t('filter.city')" />
      <div class="row">
        <button class="btn primary" type="submit">{{ t("filter.apply") }}</button>
        <button class="btn ghost" type="button" @click="clear">{{ t("filter.clear") }}</button>
      </div>
    </form>
  </section>

  <section class="grid feed">
    <ReportCard v-for="r in items" :key="r.id" :report="r" :counts="counts[r.id]" />
  </section>
  <p v-if="!loading && !items.length" class="empty">{{ t("filter.empty") }}</p>
  <p v-if="loading" class="empty">{{ t("common.loading") }}</p>
  <div v-if="items.length < total && !loading" class="center">
    <button class="btn" @click="more">{{ t("common.more") }}</button>
  </div>
</template>

<style scoped>
.hero { display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; align-items: center; margin-block-end: 22px; }
.hero h1 { font-size: clamp(24px, 3.2vw, 34px); }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; display: grid; gap: 2px; }
.stat strong { font-size: 30px; line-height: 1; }
.stat span { color: var(--muted); font-size: 13px; }
.stat.missing strong { color: var(--missing); }
.stat.found strong { color: var(--found); }
.stat.resolved strong { color: var(--primary); }
.filters { display: grid; gap: 14px; margin-block-end: 22px; }
.filter-grid { display: grid; gap: 10px; grid-template-columns: 2fr 1fr 0.8fr 0.8fr 1fr auto; }
.feed { margin-block-end: 22px; }
@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; }
  .filter-grid { grid-template-columns: 1fr 1fr; }
  .filter-grid .q { grid-column: 1 / -1; }
}
</style>
