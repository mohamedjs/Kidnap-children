<script setup lang="ts">
import { reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { ApiError, post } from "../lib/api";
import { t } from "../lib/i18n";
import { session } from "../lib/session";
import type { Me } from "../lib/types";

const props = defineProps<{ mode: "login" | "register" | "forgot" | "reset" }>();
const route = useRoute();
const router = useRouter();
const f = reactive({ email: "", password: "", name: "", phone: "", city: "" });
const error = ref("");
const done = ref("");
const busy = ref(false);

async function submit() {
  error.value = "";
  busy.value = true;
  try {
    if (props.mode === "login" || props.mode === "register") {
      const body = props.mode === "login" ? { email: f.email, password: f.password } : f;
      const res = await post<{ token: string; user: Me }>(`/api/auth/${props.mode}`, body);
      session.set(res.token, res.user);
      router.push((route.query.next as string) || "/");
    } else if (props.mode === "forgot") {
      await post("/api/auth/password/forgot", { email: f.email });
      done.value = t("auth.forgotSent");
    } else {
      await post("/api/auth/password/reset", { token: route.query.token, password: f.password });
      done.value = t("auth.resetDone");
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : t("common.error");
  } finally {
    busy.value = false;
  }
}

const titles = { login: "auth.loginTitle", register: "auth.registerTitle", forgot: "auth.forgotTitle", reset: "auth.resetTitle" } as const;
</script>

<template>
  <form class="card pad stack auth" @submit.prevent="submit">
    <h1>{{ t(titles[props.mode]) }}</h1>
    <template v-if="props.mode === 'register'">
      <label class="field">{{ t("auth.name") }}<input v-model="f.name" class="input" required maxlength="80" autocomplete="name" /></label>
    </template>
    <label v-if="props.mode !== 'reset'" class="field">{{ t("auth.email") }}<input v-model="f.email" class="input" type="email" required dir="ltr" autocomplete="email" /></label>
    <label v-if="props.mode !== 'forgot'" class="field">{{ t("auth.password") }}<input v-model="f.password" class="input" type="password" required minlength="8" dir="ltr" :autocomplete="props.mode === 'login' ? 'current-password' : 'new-password'" /></label>
    <template v-if="props.mode === 'register'">
      <div class="fields">
        <label class="field">{{ t("auth.phone") }}<input v-model="f.phone" class="input" dir="ltr" autocomplete="tel" /></label>
        <label class="field">{{ t("auth.city") }}<input v-model="f.city" class="input" /></label>
      </div>
    </template>
    <p v-if="error" class="alert error">{{ error }}</p>
    <p v-if="done" class="alert ok">{{ done }}</p>
    <button class="btn primary" :disabled="busy">
      {{ props.mode === "login" ? t("auth.submitLogin") : props.mode === "register" ? t("auth.submitRegister") : props.mode === "forgot" ? t("auth.forgotSend") : t("form.save") }}
    </button>
    <p class="muted small center">
      <template v-if="props.mode === 'login'">
        {{ t("auth.noAccount") }} <RouterLink to="/register">{{ t("nav.register") }}</RouterLink> ·
        <RouterLink to="/forgot-password">{{ t("auth.forgot") }}</RouterLink>
      </template>
      <template v-else>{{ t("auth.haveAccount") }} <RouterLink to="/login">{{ t("nav.login") }}</RouterLink></template>
    </p>
  </form>
</template>

<style scoped>
.auth { max-inline-size: 460px; margin: 30px auto; }
</style>
