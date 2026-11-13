<script setup lang="ts">
// v1: the post card inside HomeComponent / Found- and MissedPersonComponent
import { RouterLink } from "vue-router";
import { fmtDate, t, timeAgo } from "../lib/i18n";
import { ageText, childTitle, placeText } from "../lib/format";
import type { Counts, Report } from "../lib/types";

defineProps<{ report: Report; counts?: Counts }>();
</script>

<template>
  <RouterLink :to="`/reports/${report.id}`" class="card report-card" :data-kind="report.kind">
    <div class="media">
      <img v-if="report.photos[0]" :src="report.photos[0].url" :alt="childTitle(report)" class="photo" loading="lazy" />
      <div v-else class="photo placeholder">?</div>
      <span class="chip kind" :class="report.status === 'resolved' ? 'resolved' : report.kind">
        {{ report.status === "resolved" ? t("status.resolved") : t(`kind.${report.kind}`) }}
      </span>
      <span v-if="report.photos.length > 1" class="chip count">+{{ report.photos.length - 1 }}</span>
    </div>
    <div class="body">
      <h3>{{ childTitle(report) }}</h3>
      <p class="facts muted small">
        <span v-if="report.gender">{{ t(`gender.${report.gender}`) }} · </span>{{ ageText(report) }} · {{ placeText(report) }}
      </p>
      <p class="desc">{{ report.description }}</p>
      <div class="row spread small muted foot">
        <span v-if="report.seen_on">{{ t(`report.seenOn.${report.kind}`) }}: {{ fmtDate(report.seen_on) }}</span>
        <span v-else>{{ timeAgo(report.created_at) }}</span>
        <span v-if="counts" class="row">
          <span>♥ {{ counts.likes }}</span>
          <span>💬 {{ counts.comments }}</span>
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.report-card { display: flex; flex-direction: column; overflow: hidden; color: var(--text); transition: transform 0.15s, border-color 0.15s; }
.report-card:hover { transform: translateY(-2px); border-color: var(--primary); text-decoration: none; }
.media { position: relative; }
.media .photo { border-radius: 0; aspect-ratio: 4 / 3; }
.placeholder { display: grid; place-items: center; font-size: 48px; color: var(--muted); }
.kind { position: absolute; inset-block-start: 12px; inset-inline-start: 12px; backdrop-filter: blur(6px); }
.count { position: absolute; inset-block-start: 12px; inset-inline-end: 12px; background: rgba(15, 23, 42, 0.6); color: #fff; border: 0; }
.body { padding: 14px 16px 16px; display: grid; gap: 4px; flex: 1; }
h3 { margin: 0; font-size: 17px; }
.facts { margin: 0; }
.desc { margin: 4px 0 0; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-size: 14px; }
.foot { margin-block-start: auto; padding-block-start: 8px; }
</style>
