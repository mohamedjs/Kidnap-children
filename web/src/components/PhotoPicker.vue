<script setup lang="ts">
// Picks images and uploads each one straight to the bucket through a presigned PUT.
// Emits the confirmed upload ids; the report form sends only those ids to the API.
import { ref } from "vue";
import { t } from "../lib/i18n";
import { LIMITS, uploadFile, UploadError, type Purpose } from "../lib/upload";

const props = withDefaults(defineProps<{ purpose?: Purpose; max?: number; existing?: number }>(), {
  purpose: "report_photo", max: 6, existing: 0,
});
const emit = defineEmits<{ (e: "change", ids: string[]): void; (e: "busy", busy: boolean): void }>();

interface Item { key: string; preview: string; progress: number; uploadId?: string; error?: string }
const items = ref<Item[]>([]);
const input = ref<HTMLInputElement>();

function sync() {
  emit("change", items.value.filter((i) => i.uploadId).map((i) => i.uploadId!));
  emit("busy", items.value.some((i) => !i.uploadId && !i.error));
}

async function onFiles(e: Event) {
  const files = Array.from((e.target as HTMLInputElement).files ?? []);
  const room = props.max - props.existing - items.value.length;
  for (const file of files.slice(0, Math.max(0, room))) {
    items.value.push({ key: crypto.randomUUID(), preview: URL.createObjectURL(file), progress: 0 });
    const live = items.value[items.value.length - 1];
    sync();
    try {
      const res = await uploadFile(file, props.purpose, (p) => (live.progress = p));
      live.uploadId = res.upload_id;
      live.progress = 100;
    } catch (err) {
      const code = err instanceof UploadError ? err.code : "network";
      live.error = t(`upload.${code}` as "upload.type");
    }
    sync();
  }
  if (input.value) input.value.value = "";
}

function remove(key: string) {
  items.value = items.value.filter((i) => i.key !== key);
  sync();
}
</script>

<template>
  <div class="picker">
    <div class="tiles">
      <div v-for="i in items" :key="i.key" class="tile" :class="{ err: i.error }">
        <img :src="i.preview" alt="" />
        <div v-if="!i.uploadId && !i.error" class="progress"><span :style="{ inlineSize: i.progress + '%' }" /></div>
        <div v-if="i.error" class="error small">{{ i.error }}</div>
        <button type="button" class="x" @click="remove(i.key)" aria-label="remove">×</button>
      </div>
      <label v-if="existing + items.length < max" class="tile add">
        <input ref="input" type="file" :accept="LIMITS[purpose].types.join(',')" multiple @change="onFiles" hidden />
        <span>＋</span>
        <small>{{ t("form.addPhoto") }}</small>
      </label>
    </div>
  </div>
</template>

<style scoped>
.tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.tile { position: relative; aspect-ratio: 1; border-radius: var(--radius-sm); overflow: hidden; background: var(--surface-2); border: 1px solid var(--border); }
.tile img { inline-size: 100%; block-size: 100%; object-fit: cover; }
.tile.err { border-color: var(--danger); }
.add { display: grid; place-content: center; text-align: center; cursor: pointer; color: var(--muted); border-style: dashed; }
.add span { font-size: 28px; }
.progress { position: absolute; inset-inline: 8px; inset-block-end: 8px; block-size: 6px; border-radius: 999px; background: rgba(0, 0, 0, 0.4); overflow: hidden; }
.progress span { display: block; block-size: 100%; background: var(--primary); transition: inline-size 0.2s; }
.error { position: absolute; inset-inline: 0; inset-block-end: 0; padding: 4px 6px; background: rgba(220, 38, 38, 0.85); color: #fff; }
.x { position: absolute; inset-block-start: 6px; inset-inline-end: 6px; inline-size: 26px; block-size: 26px; border-radius: 50%; border: 0; background: rgba(15, 23, 42, 0.7); color: #fff; cursor: pointer; }
</style>
