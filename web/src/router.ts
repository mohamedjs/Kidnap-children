import { createRouter, createWebHistory } from "vue-router";
import { session } from "./lib/session";

export const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: "/", component: () => import("./views/HomeView.vue") },
    { path: "/reports/new", component: () => import("./views/NewReportView.vue"), meta: { auth: true } },
    { path: "/reports/:id", component: () => import("./views/ReportView.vue"), props: true },
    { path: "/reports/:id/edit", component: () => import("./views/NewReportView.vue"), props: true, meta: { auth: true } },
    { path: "/matches", component: () => import("./views/MatchesView.vue"), meta: { auth: true } },
    { path: "/messages/:userId?", component: () => import("./views/MessagesView.vue"), props: true, meta: { auth: true } },
    { path: "/notifications", component: () => import("./views/NotificationsView.vue"), meta: { auth: true } },
    { path: "/users/:id", component: () => import("./views/ProfileView.vue"), props: true },
    { path: "/me", component: () => import("./views/ProfileView.vue"), meta: { auth: true } },
    { path: "/admin", component: () => import("./views/AdminView.vue"), meta: { auth: true, admin: true } },
    { path: "/login", component: () => import("./views/AuthView.vue"), props: { mode: "login" } },
    { path: "/register", component: () => import("./views/AuthView.vue"), props: { mode: "register" } },
    { path: "/forgot-password", component: () => import("./views/AuthView.vue"), props: { mode: "forgot" } },
    { path: "/reset-password", component: () => import("./views/AuthView.vue"), props: { mode: "reset" } },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

router.beforeEach((to) => {
  if (to.meta.auth && !session.token) return { path: "/login", query: { next: to.fullPath } };
  if (to.meta.admin && !session.isAdmin) return "/";
  return true;
});
