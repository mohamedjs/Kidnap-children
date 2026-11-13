<script setup lang="ts">
// v1 InnerPostComponent: one report with photos, comments, likes; owner tools; matches.
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import MatchPair from "../components/MatchPair.vue";
import { ApiError, del, get, post } from "../lib/api";
import { ageText, childTitle, placeText } from "../lib/format";
import { fmtDate, t, timeAgo } from "../lib/i18n";
import { session } from "../lib/session";
import type { Comment, Counts, Match, Paged, Report } from "../lib/types";

const props = defineProps<{ id: string }>();
const router = useRouter();
const report = ref<Report | null>(null);
const counts = ref<Counts>({ comments: 0, likes: 0, liked: false });
const comments = ref<Comment[]>([]);
const matches = ref<Match[]>([]);
const active = ref(0);
const body = ref("");
const notice = ref("");
const error = ref("");
const flagOpen = ref(false);
const flag = ref({ reason: "fake", note: "" });

const mine = computed(() => report.value?.can_edit ?? false);

async function load() {
  try {
    report.value = await get<Report>(`/api/reports/${props.id}`);
  } catch (e) {
    error.value = e instanceof ApiError && e.status === 404 ? "404" : t("common.error");
    return;
  }
  counts.value = (await get<Record<string, Counts>>("/api/engagement", { report_ids: props.id }))[props.id];
  comments.value = (await get<Paged<Comment>>(`/api/reports/${props.id}/comments`)).items;
  if (mine.value) matches.value = await get<Match[]>(`/api/reports/${props.id}/matches`);
}

async function like() {
  if (!session.token) return router.push(`/login?next=/reports/${props.id}`);
  counts.value = await post<Counts>(`/api/reports/${props.id}/like`);
}

async function addComment() {
  if (!body.value.trim()) return;
  const c = await post<Comment>(`/api/reports/${props.id}/comments`, { body: body.value });
  comments.value.push(c);
  counts.value.comments += 1;
  body.value = "";
}

async function removeComment(c: Comment) {
  await del(`/api/comments/${c.id}`);
  comments.value = comments.value.filter((x) => x.id !== c.id);
  counts.value.comments -= 1;
}

async function act(action: "resolve" | "reopen" | "rematch") {
  const res = await post<Report | { queued: boolean }>(`/api/reports/${props.id}/${action}`);
  if (action === "rematch") notice.value = t("report.rematchQueued");
  else report.value = res as Report;
}

async function remove() {
  if (!confirm(t("report.deleteConfirm"))) return;
  await del(`/api/reports/${props.id}`);
  router.push("/");
}

async function sendFlag() {
  await post(`/api/reports/${props.id}/flag`, flag.value);
  flagOpen.value = false;
  notice.value = t("flag.sent");
}

async function copyLink() {
  await navigator.clipboard?.writeText(location.href);
  notice.value = t("report.copied");
}

const canDelete = (c: Comment) =>
  session.user && (c.author?.id === session.user.id || mine.value || session.isAdmin);

onMounted(load);
</script>

<template>
  <p v-if="error" class="empty">{{ error === "404" ? "404" : error }}</p>
  <div v-else-if="!report" class="empty">{{ t("common.loading") }}</div>
  <article v-else class="layout">
    <section class="gallery card">
      <img v-if="report.photos[active]" :src="report.photos[active].url" :alt="childTitle(report)" class="main" />
      <div v-else class="main placeholder">?</div>
      <div v-if="report.photos.length > 1" class="thumbs">
        <button v-for="(p, i) in report.photos" :key="p.id" :class="{ on: i === active }" @click="active = i">
          <img :src="p.url" alt="" />
        </button>
      </div>
      <p class="muted small note">🔒 {{ t("report.photoNote") }}</p>
    </section>

    <section class="info stack">
      <div v-if="report.status === 'hidden'" class="alert error">{{ t("report.hiddenBanner") }}: {{ report.hidden_reason }}</div>
      <div v-if="notice" class="alert ok">{{ notice }}</div>
      <div class="row">
        <span class="chip" :class="report.kind">{{ t(`kind.${report.kind}`) }}</span>
        <span class="chip" :class="report.status">{{ t(`status.${report.status}`) }}</span>
      </div>
      <h1>{{ childTitle(report) }}</h1>
      <dl class="facts">
        <div v-if="report.gender"><dt>{{ t("form.gender") }}</dt><dd>{{ t(`gender.${report.gender}`) }}</dd></div>
        <div><dt>{{ t("form.age") }}</dt><dd>{{ ageText(report) }}</dd></div>
        <div><dt>{{ t("form.city") }}</dt><dd>{{ placeText(report) }}</dd></div>
        <div v-if="report.seen_on"><dt>{{ t(`report.seenOn.${report.kind}`) }}</dt><dd>{{ fmtDate(report.seen_on) }}</dd></div>
        <div>
          <dt>{{ t("report.contact") }}</dt>
          <dd v-if="report.contact_phone" dir="ltr">{{ report.contact_phone }}</dd>
          <dd v-else class="muted small">{{ t("report.contactLogin") }}</dd>
        </div>
      </dl>
      <p class="desc">{{ report.description }}</p>
      <div v-if="report.owner" class="row owner">
        <RouterLink :to="`/users/${report.owner.id}`" class="row">
          <img v-if="report.owner.avatar_url" :src="report.owner.avatar_url" class="avatar" alt="" />
          <span>{{ t("report.by") }} <strong>{{ report.owner.name }}</strong></span>
        </RouterLink>
        <span class="muted small">· {{ timeAgo(report.created_at) }}</span>
      </div>
      <div class="row actions">
        <button class="btn" :class="{ primary: counts.liked }" @click="like">♥ {{ t("report.like") }} · {{ counts.likes }}</button>
        <RouterLink v-if="session.token && report.owner && !mine" :to="`/messages/${report.owner.id}`" class="btn">✉ {{ t("report.message") }}</RouterLink>
        <button class="btn ghost" @click="copyLink">🔗 {{ t("report.share") }}</button>
        <button v-if="session.token && !mine" class="btn ghost danger" @click="flagOpen = !flagOpen">⚑ {{ t("report.flag") }}</button>
      </div>
      <form v-if="flagOpen" class="card pad stack" @submit.prevent="sendFlag">
        <strong>{{ t("flag.title") }}</strong>
        <select v-model="flag.reason" class="input">
          <option v-for="r in ['fake', 'privacy', 'abuse', 'duplicate', 'other']" :key="r" :value="r">{{ t(`flag.${r}` as 'flag.fake') }}</option>
        </select>
        <input v-model="flag.note" class="input" :placeholder="t('flag.note')" />
        <button class="btn primary">{{ t("flag.send") }}</button>
      </form>
      <div v-if="mine" class="card pad row owner-tools">
        <RouterLink :to="`/reports/${report.id}/edit`" class="btn sm">✎ {{ t("profile.edit") }}</RouterLink>
        <button v-if="report.status === 'open'" class="btn sm primary" @click="act('resolve')">✓ {{ t("report.resolve") }}</button>
        <button v-if="report.status === 'resolved'" class="btn sm" @click="act('reopen')">{{ t("report.reopen") }}</button>
        <button v-if="report.status === 'open'" class="btn sm" @click="act('rematch')">↻ {{ t("report.rematch") }}</button>
        <button class="btn sm ghost danger" @click="remove">{{ t("report.delete") }}</button>
      </div>
    </section>

    <section v-if="mine" class="wide stack">
      <h2>{{ t("report.matches") }}</h2>
      <p v-if="!matches.length" class="muted">{{ t("report.noMatches") }}</p>
      <MatchPair v-for="m in matches" :key="m.id" :match="m" @changed="load" />
    </section>

    <section class="wide card pad stack">
      <h2>{{ t("report.comments") }} · {{ counts.comments }}</h2>
      <div v-for="c in comments" :key="c.id" class="comment">
        <img v-if="c.author?.avatar_url" :src="c.author.avatar_url" class="avatar" alt="" />
        <div class="bubble">
          <div class="row spread small"><strong>{{ c.author?.name }}</strong><span class="muted">{{ timeAgo(c.created_at) }}</span></div>
          <p>{{ c.body }}</p>
          <button v-if="canDelete(c)" class="link small" @click="removeComment(c)">{{ t("comment.delete") }}</button>
        </div>
      </div>
      <form v-if="session.token" class="row" @submit.prevent="addComment">
        <input v-model="body" class="input grow" :placeholder="t('comment.placeholder')" maxlength="1000" />
        <button class="btn primary">{{ t("comment.send") }}</button>
      </form>
      <RouterLink v-else :to="`/login?next=/reports/${report.id}`" class="muted">{{ t("comment.loginToComment") }}</RouterLink>
    </section>
  </article>
</template>

<style scoped>
.layout { display: grid; grid-template-columns: 1.1fr 1fr; gap: 24px; align-items: start; }
.wide { grid-column: 1 / -1; }
.gallery { padding: 12px; display: grid; gap: 10px; }
.main { inline-size: 100%; aspect-ratio: 1; object-fit: cover; border-radius: var(--radius-sm); background: var(--surface-2); }
.placeholder { display: grid; place-items: center; font-size: 64px; color: var(--muted); }
.thumbs { display: flex; gap: 8px; flex-wrap: wrap; }
.thumbs button { padding: 0; border: 2px solid transparent; border-radius: 10px; overflow: hidden; cursor: pointer; background: none; }
.thumbs button.on { border-color: var(--primary); }
.thumbs img { inline-size: 72px; block-size: 72px; object-fit: cover; }
.note { margin: 0; }
h1 { font-size: 30px; margin: 0; }
.facts { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 0; }
.facts div { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 10px 12px; }
.facts dt { color: var(--muted); font-size: 12px; }
.facts dd { margin: 0; font-weight: 600; }
.desc { white-space: pre-line; margin: 0; }
.owner a { color: var(--text); }
.comment { display: flex; gap: 10px; align-items: flex-start; }
.bubble { background: var(--surface-2); border-radius: var(--radius-sm); padding: 8px 12px; flex: 1; }
.bubble p { margin: 2px 0 0; }
.link { background: none; border: 0; color: var(--danger); cursor: pointer; padding: 0; }
.grow { flex: 1; inline-size: auto; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
