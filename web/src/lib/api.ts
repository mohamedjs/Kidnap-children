// The only way the web app reaches data: the FastAPI `/api/*` endpoints.
import { session } from "./session";

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}

type Query = Record<string, string | number | boolean | null | undefined>;

function qs(params?: Query): string {
  if (!params) return "";
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== null && v !== "") p.set(k, String(v));
  const s = p.toString();
  return s ? `?${s}` : "";
}

export async function api<T = unknown>(method: string, path: string, body?: unknown, params?: Query): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (session.token) headers.Authorization = `Bearer ${session.token}`;
  const res = await fetch(`${path}${qs(params)}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  if (res.status === 204) return undefined as T;
  const json = await res.json().catch(() => null);
  if (!res.ok || !json?.success) {
    if (res.status === 401 && session.token) session.clear();
    throw new ApiError(res.status, json?.error?.code ?? "http_error", json?.error?.message ?? res.statusText);
  }
  return json.data as T;
}

export const get = <T>(path: string, params?: Query) => api<T>("GET", path, undefined, params);
export const post = <T>(path: string, body?: unknown) => api<T>("POST", path, body ?? {});
export const patch = <T>(path: string, body: unknown) => api<T>("PATCH", path, body);
export const del = (path: string) => api<void>("DELETE", path);
