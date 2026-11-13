<script setup lang="ts">
import { onMounted, ref } from "vue";
import MatchPair from "../components/MatchPair.vue";
import { get } from "../lib/api";
import { t } from "../lib/i18n";
import type { Match } from "../lib/types";

const matches = ref<Match[] | null>(null);
async function load() {
  matches.value = await get<Match[]>("/api/matches");
}
onMounted(load);
</script>

<template>
  <h1>{{ t("matches.title") }}</h1>
  <p class="muted">{{ t("matches.subtitle") }}</p>
  <p v-if="matches === null" class="empty">{{ t("common.loading") }}</p>
  <p v-else-if="!matches.length" class="empty">{{ t("matches.empty") }}</p>
  <div v-else class="stack">
    <MatchPair v-for="m in matches" :key="m.id" :match="m" @changed="load" />
  </div>
</template>
