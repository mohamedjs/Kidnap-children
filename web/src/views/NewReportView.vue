<script setup lang="ts">
// New / edit report. Photos are uploaded by PhotoPicker (presigned PUT) before submit;
// the API only receives the confirmed upload ids.
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import PhotoPicker from "../components/PhotoPicker.vue";
import { ApiError, get, patch, post } from "../lib/api";
import { t } from "../lib/i18n";
import { session } from "../lib/session";
import type { Kind, Report } from "../lib/types";

const props = defineProps<{ id?: string }>();
const router = useRouter();
const form = reactive({
  kind: "missing" as Kind, child_name: "", gender: "" as "" | "male" | "female", age: "" as string | number,
  description: "", city: session.user?.city ?? "", area: "", seen_on: "", contact_phone: session.user?.phone ?? "",
  lat: null as number | null, lng: null as number | null,
});
const uploads = ref<string[]>([]);
const removeIds = ref<string[]>([]);
const existing = ref<Report | null>(null);
const busy = ref(false);
const saving = ref(false);
const error = ref("");
const today = new Date().toISOString().slice(0, 10);
const keptPhotos = computed(() => (existing.value?.photos ?? []).filter((p) => !removeIds.value.includes(p.id)));

onMounted(async () => {
  if (!props.id) return;
  const r = await get<Report>(`/api/reports/${props.id}`);
  existing.value = r;
  Object.assign(form, {
    kind: r.kind, child_name: r.child_name ?? "", gender: r.gender ?? "", age: r.age ?? "", description: r.description,
    city: r.city, area: r.area ?? "", seen_on: r.seen_on ?? "", contact_phone: r.contact_phone ?? "", lat: r.lat, lng: r.lng,
  });
});

function locate() {
  navigator.geolocation?.getCurrentPosition((p) => {
    form.lat = Number(p.coords.latitude.toFixed(5));
    form.lng = Number(p.coords.longitude.toFixed(5));
  });
}

function payload() {
  return {
    kind: form.kind, child_name: form.child_name || null, gender: form.gender || null,
    age: form.age === "" ? null : Number(form.age), description: form.description, city: form.city,
    area: form.area || null, seen_on: form.seen_on || null, contact_phone: form.contact_phone || null,
    lat: form.lat, lng: form.lng,
  };
}

async function submit() {
  error.value = "";
  saving.value = true;
  try {
    const r = props.id
      ? await patch<Report>(`/api/reports/${props.id}`, { report: payload(), add_photo_upload_ids: uploads.value, remove_photo_ids: removeIds.value })
      : await post<Report>("/api/reports", { ...payload(), photo_upload_ids: uploads.value });
    router.push(`/reports/${r.id}`);
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : t("common.error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <form class="card pad stack form" @submit.prevent="submit">
    <h1>{{ props.id ? t("profile.edit") : t("form.newTitle") }}</h1>
    <div v-if="!props.id" class="segmented">
      <button type="button" :class="{ on: form.kind === 'missing' }" @click="form.kind = 'missing'">{{ t("form.kind.missing") }}</button>
      <button type="button" :class="{ on: form.kind === 'found' }" @click="form.kind = 'found'">{{ t("form.kind.found") }}</button>
    </div>
    <div class="fields">
      <label class="field">{{ form.kind === "missing" ? t("form.childName") : t("form.childNameFound") }}
        <input v-model="form.child_name" class="input" :required="form.kind === 'missing'" maxlength="80" />
      </label>
      <label class="field">{{ t("form.gender") }}
        <select v-model="form.gender" class="input">
          <option value="">—</option>
          <option value="male">{{ t("gender.male") }}</option>
          <option value="female">{{ t("gender.female") }}</option>
        </select>
      </label>
      <label class="field">{{ t("form.age") }}
        <input v-model="form.age" class="input" type="number" min="0" max="17" />
      </label>
      <label class="field">{{ t(`form.seenOn.${form.kind}`) }}
        <input v-model="form.seen_on" class="input" type="date" :max="today" />
      </label>
      <label class="field">{{ t("form.city") }}
        <input v-model="form.city" class="input" required maxlength="80" />
      </label>
      <label class="field">{{ t("form.area") }}
        <input v-model="form.area" class="input" maxlength="80" />
      </label>
      <label class="field">{{ t("form.phone") }}
        <input v-model="form.contact_phone" class="input" dir="ltr" maxlength="30" />
      </label>
      <div class="field">{{ t("form.location") }}
        <div class="row">
          <button type="button" class="btn sm" @click="locate">📍 {{ t("form.useMyLocation") }}</button>
          <span v-if="form.lat !== null" class="muted small" dir="ltr">{{ form.lat }}, {{ form.lng }}</span>
        </div>
      </div>
    </div>
    <label class="field">{{ t("form.description") }}
      <span class="hint muted small">{{ t("form.descriptionHint") }}</span>
      <textarea v-model="form.description" class="input" required minlength="10" maxlength="4000" />
    </label>
    <div class="field">{{ t("form.photos") }}
      <span class="hint muted small">{{ t("form.photosHint") }}</span>
      <div v-if="keptPhotos.length" class="kept">
        <div v-for="p in keptPhotos" :key="p.id" class="kept-item">
          <img :src="p.url" alt="" />
          <button type="button" @click="removeIds.push(p.id)" aria-label="remove">×</button>
        </div>
      </div>
      <PhotoPicker :existing="keptPhotos.length" @change="uploads = $event" @busy="busy = $event" />
    </div>
    <p v-if="error" class="alert error">{{ error }}</p>
    <div class="row">
      <button class="btn primary" :disabled="busy || saving">{{ busy ? t("form.uploading") : props.id ? t("form.save") : t("form.submit") }}</button>
      <button type="button" class="btn ghost" @click="router.back()">{{ t("form.cancel") }}</button>
    </div>
  </form>
</template>

<style scoped>
.form { max-inline-size: 860px; margin-inline: auto; }
.kept { display: flex; gap: 10px; flex-wrap: wrap; }
.kept-item { position: relative; }
.kept-item img { inline-size: 110px; block-size: 110px; object-fit: cover; border-radius: var(--radius-sm); }
.kept-item button { position: absolute; inset-block-start: 6px; inset-inline-end: 6px; border: 0; border-radius: 50%; inline-size: 26px; block-size: 26px; background: rgba(15, 23, 42, 0.7); color: #fff; cursor: pointer; }
</style>
