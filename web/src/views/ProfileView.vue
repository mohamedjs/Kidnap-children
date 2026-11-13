<script setup lang="ts">
// v1 ProfileComponent + FoundPersonComponent + MissedPersonComponent: cover, avatar,
// and the user's missing / found reports. Avatar and cover upload via presigned PUT.
import { computed, onMounted, reactive, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import ReportCard from "../components/ReportCard.vue";
import { get, patch } from "../lib/api";
import { fmtDate, t } from "../lib/i18n";
import { session } from "../lib/session";
import type { Me, Paged, PublicUser, Report } from "../lib/types";
import { uploadFile, UploadError } from "../lib/upload";

const props = defineProps<{ id?: string }>();
const userId = computed(() => props.id ?? session.user?.id ?? "");
const isMe = computed(() => !!session.user && userId.value === session.user.id);
const user = ref<PublicUser | null>(null);
const tab = ref<"missing" | "found">("missing");
const reports = ref<Report[]>([]);
const editing = ref(false);
const form = reactive({ name: "", city: "", phone: "", bio: "" });
const notice = ref("");
const error = ref("");

async function load() {
  if (!userId.value) return;
  user.value = isMe.value ? await get<Me>("/api/auth/me") : await get<PublicUser>(`/api/users/${userId.value}`);
  await loadReports();
}

async function loadReports() {
  reports.value = (await get<Paged<Report>>("/api/reports", { owner_id: userId.value, kind: tab.value, per_page: 50 })).items;
}

function startEdit() {
  const me = user.value as Me;
  Object.assign(form, { name: me.name, city: me.city ?? "", phone: me.phone ?? "", bio: me.bio ?? "" });
  editing.value = true;
}

async function save(extra: Record<string, string> = {}) {
  const me = await patch<Me>("/api/profile", { ...(editing.value ? form : {}), ...extra });
  session.setUser(me);
  user.value = me;
  editing.value = false;
  notice.value = t("profile.saved");
}

async function changeImage(e: Event, purpose: "avatar" | "cover") {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  error.value = "";
  try {
    const up = await uploadFile(file, purpose);
    await save({ [`${purpose}_upload_id`]: up.upload_id });
  } catch (err) {
    error.value = t(`upload.${err instanceof UploadError ? err.code : "network"}` as "upload.type");
  }
}

watch(tab, loadReports);
watch(userId, load);
onMounted(load);
</script>

<template>
  <div v-if="!user" class="empty">{{ t("common.loading") }}</div>
  <template v-else>
    <section class="card profile">
      <div class="cover" :style="user.cover_url ? { backgroundImage: `url(${user.cover_url})` } : {}">
        <label v-if="isMe" class="btn sm change-cover">🖼 {{ t("profile.cover") }}<input type="file" accept="image/jpeg,image/png,image/webp" hidden @change="changeImage($event, 'cover')" /></label>
      </div>
      <div class="who">
        <label class="avatar-wrap" :class="{ editable: isMe }">
          <img v-if="user.avatar_url" :src="user.avatar_url" class="avatar lg" alt="" />
          <span v-else class="avatar lg" />
          <input v-if="isMe" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="changeImage($event, 'avatar')" />
        </label>
        <div class="grow">
          <h1>{{ user.name }}</h1>
          <p class="muted small">{{ user.city }}<template v-if="user.created_at"> · {{ t("profile.memberSince") }} {{ fmtDate(user.created_at) }}</template></p>
          <p v-if="user.bio">{{ user.bio }}</p>
        </div>
        <div class="row">
          <button v-if="isMe && !editing" class="btn sm" @click="startEdit">✎ {{ t("profile.edit") }}</button>
          <RouterLink v-if="!isMe && session.token" :to="`/messages/${user.id}`" class="btn sm primary">✉ {{ t("report.message") }}</RouterLink>
        </div>
      </div>
      <p v-if="notice" class="alert ok">{{ notice }}</p>
      <p v-if="error" class="alert error">{{ error }}</p>
      <form v-if="editing" class="pad stack" @submit.prevent="save()">
        <div class="fields">
          <label class="field">{{ t("auth.name") }}<input v-model="form.name" class="input" required /></label>
          <label class="field">{{ t("auth.city") }}<input v-model="form.city" class="input" /></label>
          <label class="field">{{ t("auth.phone") }}<input v-model="form.phone" class="input" dir="ltr" /></label>
        </div>
        <label class="field">{{ t("profile.bio") }}<textarea v-model="form.bio" class="input" maxlength="500" /></label>
        <div class="row">
          <button class="btn primary">{{ t("form.save") }}</button>
          <button type="button" class="btn ghost" @click="editing = false">{{ t("form.cancel") }}</button>
        </div>
      </form>
    </section>

    <div class="segmented tabs">
      <button :class="{ on: tab === 'missing' }" @click="tab = 'missing'">{{ t("profile.missingTab") }}</button>
      <button :class="{ on: tab === 'found' }" @click="tab = 'found'">{{ t("profile.foundTab") }}</button>
    </div>
    <section class="grid">
      <ReportCard v-for="r in reports" :key="r.id" :report="r" />
    </section>
    <p v-if="!reports.length" class="empty">{{ t("filter.empty") }}</p>
  </template>
</template>

<style scoped>
.profile { overflow: hidden; margin-block-end: 20px; }
.cover { block-size: 200px; background: linear-gradient(120deg, var(--primary-strong), var(--found)); background-size: cover; background-position: center; position: relative; }
.change-cover { position: absolute; inset-block-end: 12px; inset-inline-end: 12px; }
.who { display: flex; gap: 16px; align-items: flex-end; padding: 0 20px 18px; margin-block-start: -40px; flex-wrap: wrap; }
.avatar-wrap.editable { cursor: pointer; }
.grow { flex: 1; min-inline-size: 200px; }
h1 { margin: 0; }
.tabs { margin-block-end: 16px; }
</style>
