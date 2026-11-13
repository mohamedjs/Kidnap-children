export interface UserSummary {
  id: string;
  name: string;
  city: string | null;
  avatar_url: string | null;
}

export interface PublicUser extends UserSummary {
  bio: string | null;
  gender: string | null;
  cover_url: string | null;
  created_at: string | null;
}

export interface Me extends PublicUser {
  email: string;
  phone: string | null;
  role: "user" | "admin";
  is_active: boolean;
  birth_date: string | null;
}

export type Kind = "missing" | "found";
export type Status = "open" | "resolved" | "hidden";

export interface Photo {
  id: string;
  url: string;
  face_status: "pending" | "face" | "no_face" | "failed";
}

export interface Report {
  id: string;
  kind: Kind;
  status: Status;
  child_name: string | null;
  gender: "male" | "female" | null;
  age: number | null;
  description: string;
  city: string;
  area: string | null;
  lat: number | null;
  lng: number | null;
  seen_on: string | null;
  contact_phone: string | null;
  hidden_reason: string | null;
  photos: Photo[];
  owner: UserSummary | null;
  can_edit: boolean;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface Paged<T> {
  items: T[];
  page: number;
  per_page: number;
  total: number;
}

export interface Counts {
  comments: number;
  likes: number;
  liked: boolean;
}

export interface Comment {
  id: string;
  report_id: string;
  body: string;
  author: UserSummary | null;
  created_at: string;
}

export interface Match {
  id: string;
  score: number;
  attribute_score: number;
  face_score: number | null;
  reasons: string[];
  status: "suggested" | "confirmed" | "dismissed";
  missing: Report;
  found: Report;
  created_at: string;
}

export interface Message {
  id: string;
  sender_id: string;
  recipient_id: string;
  body: string | null;
  attachment: { url: string; content_type: string; name: string | null; size: number } | null;
  read_at: string | null;
  created_at: string;
}

export interface Conversation {
  user: UserSummary;
  last_message: Message;
  unread_count: number;
}

export interface AppNotification {
  id: string;
  type: "comment" | "like" | "message" | "match" | "match_confirmed";
  link: string;
  data: Record<string, unknown>;
  actor: UserSummary | null;
  read: boolean;
  created_at: string;
}
