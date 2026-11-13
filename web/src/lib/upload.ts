// Presigned uploads: the file goes straight from the browser to the bucket.
// 1) ask the API for a PUT URL  2) PUT the bytes  3) confirm the upload id.
import { post } from "./api";

export type Purpose = "report_photo" | "avatar" | "cover" | "message_attachment";

export const LIMITS: Record<Purpose, { types: string[]; maxMb: number }> = {
  report_photo: { types: ["image/jpeg", "image/png", "image/webp"], maxMb: 8 },
  avatar: { types: ["image/jpeg", "image/png", "image/webp"], maxMb: 5 },
  cover: { types: ["image/jpeg", "image/png", "image/webp"], maxMb: 8 },
  message_attachment: { types: ["image/jpeg", "image/png", "image/webp", "application/pdf"], maxMb: 10 },
};

interface Ticket {
  upload_id: string;
  url: string;
  method: string;
  headers: Record<string, string>;
}

export interface Uploaded {
  upload_id: string;
  url: string;
  content_type: string;
  size: number;
}

export class UploadError extends Error {
  constructor(public code: "type" | "size" | "network" | "rejected") {
    super(code);
  }
}

function putWithProgress(t: Ticket, file: File, onProgress?: (p: number) => void): Promise<number> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(t.method, t.url);
    for (const [k, v] of Object.entries(t.headers)) xhr.setRequestHeader(k, v);
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress?.(Math.round((e.loaded / e.total) * 100));
    xhr.onload = () => resolve(xhr.status);
    xhr.onerror = () => reject(new UploadError("network"));
    xhr.send(file);
  });
}

export async function uploadFile(file: File, purpose: Purpose, onProgress?: (p: number) => void): Promise<Uploaded> {
  const rule = LIMITS[purpose];
  if (!rule.types.includes(file.type)) throw new UploadError("type");
  if (file.size > rule.maxMb * 1024 * 1024) throw new UploadError("size");
  const ticket = await post<Ticket>("/api/uploads", { purpose, content_type: file.type, size: file.size, filename: file.name });
  const status = await putWithProgress(ticket, file, onProgress);
  if (status < 200 || status >= 300) throw new UploadError("network");
  try {
    return await post<Uploaded>(`/api/uploads/${ticket.upload_id}/confirm`);
  } catch {
    throw new UploadError("rejected");
  }
}
