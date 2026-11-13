<script setup lang="ts">
// v1 AiMatchComparison: the two reports side by side with the score and why they match.
import { RouterLink } from "vue-router";
import { post } from "../lib/api";
import { ageText, childTitle, placeText } from "../lib/format";
import { fmtDate, t } from "../lib/i18n";
import type { Match, Report } from "../lib/types";

const props = defineProps<{ match: Match }>();
const emit = defineEmits<{ (e: "changed"): void }>();

async function decide(action: "confirm" | "dismiss") {
  await post(`/api/matches/${props.match.id}/${action}`);
  emit("changed");
}

const sides = (m: Match): Report[] => [m.missing, m.found];
</script>

<template>
  <div class="card match" :class="match.status">
    <div class="head row spread">
      <div class="row">
        <strong>{{ t("matches.score") }}</strong>
        <span class="score">{{ Math.round(match.score) }}%</span>
        <span v-if="match.face_score !== null" class="chip">{{ t("matches.face") }}: {{ Math.round(match.face_score) }}%</span>
      </div>
      <div class="row">
        <span v-for="r in match.reasons" :key="r" class="chip">{{ t(`reason.${r}` as "reason.near") }}</span>
      </div>
    </div>
    <div class="bar"><span :style="{ inlineSize: match.score + '%' }" /></div>
    <div class="pair">
      <RouterLink v-for="r in sides(match)" :key="r.id" :to="`/reports/${r.id}`" class="side">
        <span class="chip" :class="r.kind">{{ t(`kind.${r.kind}`) }}</span>
        <img v-if="r.photos[0]" :src="r.photos[0].url" class="photo" alt="" />
        <strong>{{ childTitle(r) }}</strong>
        <span class="muted small">{{ r.gender ? t(`gender.${r.gender}`) + " · " : "" }}{{ ageText(r) }}</span>
        <span class="muted small">{{ placeText(r) }}<template v-if="r.seen_on"> · {{ fmtDate(r.seen_on) }}</template></span>
      </RouterLink>
    </div>
    <div class="row foot">
      <template v-if="match.status === 'suggested'">
        <button class="btn primary sm" @click="decide('confirm')">✓ {{ t("matches.confirm") }}</button>
        <button class="btn ghost sm" @click="decide('dismiss')">{{ t("matches.dismiss") }}</button>
      </template>
      <span v-else class="chip" :class="match.status === 'confirmed' ? 'found' : ''">
        {{ t(match.status === "confirmed" ? "matches.confirmed" : "matches.dismissed") }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.match { padding: 16px; display: grid; gap: 12px; }
.match.dismissed { opacity: 0.6; }
.score { font-size: 22px; font-weight: 700; color: var(--found); }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.side { display: grid; gap: 4px; color: var(--text); background: var(--surface-2); border-radius: var(--radius-sm); padding: 10px; justify-items: start; }
.side:hover { text-decoration: none; outline: 1px solid var(--primary); }
.side .photo { aspect-ratio: 16 / 10; max-block-size: 240px; }
</style>
