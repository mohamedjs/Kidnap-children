<script setup lang="ts">
// v1 ChatComponent: conversations list + thread; v2 adds presigned attachments.
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { get, post } from "../lib/api";
import { t, timeAgo } from "../lib/i18n";
import { session } from "../lib/session";
import type { Conversation, Message, UserSummary } from "../lib/types";
import { uploadFile, UploadError } from "../lib/upload";

const props = defineProps<{ userId?: string }>();
const convs = ref<Conversation[]>([]);
const other = ref<UserSummary | null>(null);
const messages = ref<Message[]>([]);
const body = ref("");
const sending = ref(false);
const error = ref("");
const scroller = ref<HTMLElement>();
let timer: number | undefined;

async function loadConvs() {
  convs.value = await get<Conversation[]>("/api/conversations");
}

async function loadThread() {
  if (!props.userId) return;
  const res = await get<{ user: UserSummary; messages: Message[] }>(`/api/conversations/${props.userId}/messages`);
  other.value = res.user;
  messages.value = res.messages;
  await nextTick();
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight });
}

async function send(attachment?: string) {
  if (!props.userId || (!body.value.trim() && !attachment)) return;
  sending.value = true;
  try {
    const m = await post<Message>("/api/messages", { recipient_id: props.userId, body: body.value || null, attachment_upload_id: attachment ?? null });
    messages.value.push(m);
    body.value = "";
    await nextTick();
    scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: "smooth" });
    loadConvs();
  } finally {
    sending.value = false;
  }
}

async function attach(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  error.value = "";
  try {
    const up = await uploadFile(file, "message_attachment");
    await send(up.upload_id);
  } catch (err) {
    error.value = t(`upload.${err instanceof UploadError ? err.code : "network"}` as "upload.type");
  }
}

onMounted(() => {
  loadConvs();
  loadThread();
  timer = window.setInterval(() => { loadThread(); loadConvs(); }, 10000);
});
onBeforeUnmount(() => window.clearInterval(timer));
watch(() => props.userId, loadThread);
</script>

<template>
  <h1>{{ t("messages.title") }}</h1>
  <div class="chat card">
    <aside class="list">
      <p v-if="!convs.length" class="empty small">{{ t("messages.empty") }}</p>
      <RouterLink v-for="c in convs" :key="c.user.id" :to="`/messages/${c.user.id}`" class="conv" :class="{ on: c.user.id === props.userId }">
        <img v-if="c.user.avatar_url" :src="c.user.avatar_url" class="avatar" alt="" />
        <div class="grow">
          <div class="row spread"><strong>{{ c.user.name }}</strong><span v-if="c.unread_count" class="badge">{{ c.unread_count }}</span></div>
          <p class="muted small preview">{{ c.last_message.body || "📎" }}</p>
        </div>
      </RouterLink>
    </aside>
    <section class="thread">
      <template v-if="props.userId">
        <header class="row">
          <img v-if="other?.avatar_url" :src="other.avatar_url" class="avatar" alt="" />
          <RouterLink :to="`/users/${props.userId}`"><strong>{{ other?.name }}</strong></RouterLink>
        </header>
        <div ref="scroller" class="msgs">
          <div v-for="m in messages" :key="m.id" class="msg" :class="{ me: m.sender_id === session.user?.id }">
            <a v-if="m.attachment && m.attachment.content_type.startsWith('image/')" :href="m.attachment.url" target="_blank" rel="noopener">
              <img :src="m.attachment.url" class="att" alt="" />
            </a>
            <a v-else-if="m.attachment" :href="m.attachment.url" class="file">📄 {{ m.attachment.name || "PDF" }}</a>
            <p v-if="m.body">{{ m.body }}</p>
            <span class="time small">{{ timeAgo(m.created_at) }}</span>
          </div>
        </div>
        <p v-if="error" class="alert error small">{{ error }}</p>
        <form class="row composer" @submit.prevent="send()">
          <label class="btn ghost sm" :title="t('messages.attach')">📎<input type="file" accept="image/jpeg,image/png,image/webp,application/pdf" hidden @change="attach" /></label>
          <input v-model="body" class="input grow" :placeholder="t('messages.placeholder')" maxlength="5000" />
          <button class="btn primary" :disabled="sending">{{ t("messages.send") }}</button>
        </form>
      </template>
      <p v-else class="empty">{{ t("messages.pick") }}</p>
    </section>
  </div>
</template>

<style scoped>
.chat { display: grid; grid-template-columns: 300px 1fr; min-block-size: 560px; overflow: hidden; }
.list { border-inline-end: 1px solid var(--border); overflow-y: auto; }
.conv { display: flex; gap: 10px; padding: 12px 14px; color: var(--text); border-block-end: 1px solid var(--border); }
.conv:hover, .conv.on { background: var(--surface-2); text-decoration: none; }
.grow { flex: 1; min-inline-size: 0; }
.preview { margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.thread { display: flex; flex-direction: column; min-block-size: 0; }
.thread header { padding: 12px 16px; border-block-end: 1px solid var(--border); }
.msgs { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; max-block-size: 460px; }
.msg { max-inline-size: 70%; align-self: flex-end; background: var(--surface-2); padding: 8px 12px; border-radius: 14px; border-end-end-radius: 4px; }
.msg.me { align-self: flex-start; background: var(--primary-strong); color: #fff; border-end-end-radius: 14px; border-end-start-radius: 4px; }
.msg p { margin: 0; white-space: pre-line; }
.msg .time { opacity: 0.7; }
.att { max-inline-size: 220px; border-radius: 10px; margin-block-end: 4px; }
.file { color: inherit; font-weight: 600; }
.composer { padding: 12px; border-block-start: 1px solid var(--border); }
@media (max-width: 760px) { .chat { grid-template-columns: 1fr; } .list { max-block-size: 200px; border-inline-end: 0; border-block-end: 1px solid var(--border); } }
</style>
