# n8n Automated Workflows - Integration & Marketing Pipelines

This directory contains production-ready **n8n workflow JSON blueprints** created for the **Kidnap-Children** social platform. These workflows handle real-time missing child post alerts, AI facial recognition match triggers, email/SMS notification pipelines, CRM record updates, partner network broadcasts, social media alerts, and live GeoJSON/RSS feeds.

---

## 📁 Workflow Blueprints

| Workflow File | Trigger Path / Mechanism | Purpose | Responsible Role |
|---|---|---|---|
| [`missing_child_post_alert.json`](./workflows/missing_child_post_alert.json) | Webhook: `POST /webhook/missing-child-post` | Receives instant missing child post creation events, verifies signatures, and dispatches parallel Email (SendGrid) & SMS (Twilio) emergency alerts. | n8n Integration Specialist |
| [`ai_match_trigger.json`](./workflows/ai_match_trigger.json) | Webhook: `POST /webhook/ai-match-trigger` | Receives AI facial match trigger events, verifies HMAC/AI signature, filters by confidence threshold (≥80%), dispatches high-priority Email/SMS alerts, and syncs match events back to Laravel DB. | n8n Integration Specialist |
| [`crm_partner_syndication.json`](./workflows/crm_partner_syndication.json) | Webhook: `POST /webhook/urgent-case-syndication` | Syncs urgent missing child cases with HubSpot CRM & sends structured alert webhooks to partner NGOs. | n8n Marketing Specialist |
| [`social_media_broadcast.json`](./workflows/social_media_broadcast.json) | Webhook: `POST /webhook/social-broadcast` | Broadcasts urgent alerts across Telegram, Discord Emergency Channel, Facebook Page & Twitter with tailored character formatting and photo attachments. | n8n Marketing Specialist |
| [`partner_feed_syndication.json`](./workflows/partner_feed_syndication.json) | Cron: `*/15 * * * *` / Webhook: `GET /webhook/refresh-partner-feed` | Fetches active urgent missing child posts from Laravel backend, generates GeoJSON and JSON Feed v1.1 standards for law enforcement/partner GIS systems, and updates internal distribution cache. | n8n Marketing Specialist |

---

## 🛠 Setup & Import Instructions

1. Open your **n8n instance** (e.g., `http://localhost:5678`).
2. Go to **Workflows** -> **Import from File**.
3. Select any of the JSON blueprints from `n8n/workflows/`.
4. Configure the required Environment Variables in your n8n environment or process settings.

### 🔑 Environment Variables Required

```env
# General & Security
APP_URL=http://localhost:8000
WEBHOOK_SECRET_KEY=your_webhook_secret_key
AI_WEBHOOK_SECRET=ai_service_secret_token
LOGGING_DLQ_ENDPOINT=https://api.kidnap-children.org/api/logs/n8n-dlq

# Email & SMS Pipelines
SENDGRID_API_URL=https://api.sendgrid.com/v3/mail/send
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM_ADDRESS=notifications@kidnap-children.org
ALERT_EMAIL_RECIPIENT=emergency-alerts@kidnap-children.org

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=+18005550199
EMERGENCY_SMS_RECIPIENT=+1234567890

# CRM & Partner Syndication
HUBSPOT_ACCESS_TOKEN=your_hubspot_private_app_token
CRM_HUBSPOT_API_URL=https://api.hubapi.com/crm/v3/objects/contacts
PARTNER_WEBHOOK_URL=https://partners.ngo-alert.org/api/v1/cases/broadcast
PARTNER_API_KEY=your_partner_secret_key

# Social Media Broadcasting
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_CHANNEL_ID=@KidnapChildrenAlerts
DISCORD_EMERGENCY_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
FACEBOOK_PAGE_ID=your_facebook_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token

# Feed & Cache
PARTNER_FEED_CACHE_ENDPOINT=https://api.kidnap-children.org/internal/cache-partner-feed
INTERNAL_CACHE_TOKEN=your_internal_cache_token
```

---

## 🧪 Testing Webhook Payloads

### 1. Missing Child Post Instant Alert Test

```bash
curl -X POST http://localhost:5678/webhook/missing-child-post \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_webhook_secret_key" \
  -d '{
    "post_id": "84729",
    "child_name": "Mariam Hassan",
    "age": 7,
    "gender": "female",
    "last_seen_location": "Alexandria, Egypt",
    "last_seen_date": "2026-07-28T16:30:00Z",
    "photo_url": "https://kidnap-children.org/uploads/posts/84729.jpg",
    "contact_phone": "+201100000000",
    "urgency_level": "CRITICAL",
    "description": "Child went missing near Montaza Park. Wearing a yellow dress."
  }'
```

### 2. AI Facial Match Trigger Test (High Confidence)

```bash
curl -X POST http://localhost:5678/webhook/ai-match-trigger \
  -H "Content-Type: application/json" \
  -H "X-AI-Signature: ai_service_secret_token" \
  -d '{
    "match_id": "AIM-9942",
    "source_post_id": "84729",
    "matched_post_id": "90123",
    "child_name": "Mariam Hassan",
    "similarity_score": 0.94,
    "source_image_url": "https://kidnap-children.org/uploads/posts/84729.jpg",
    "matched_image_url": "https://kidnap-children.org/uploads/matches/90123.jpg",
    "matched_location": "Giza, Egypt",
    "guardian_email": "family@example.com",
    "guardian_phone": "+201100000000"
  }'
```

### 3. Urgent Case CRM & Partner Broadcast Test

```bash
curl -X POST http://localhost:5678/webhook/urgent-case-syndication \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "10293",
    "child_name": "Sami Ahmed",
    "age": 6,
    "gender": "male",
    "last_seen_date": "2026-07-28T14:00:00Z",
    "last_seen_location": "Cairo, Egypt",
    "contact_phone": "+201000000000",
    "case_url": "https://kidnap-children.org/posts/10293",
    "image_url": "https://kidnap-children.org/uploads/posts/10293.jpg",
    "description": "Child missing since 2 PM near City Park.",
    "priority": "HIGH_ALERT"
  }'
```

### 4. Social Media Broadcast Test

```bash
curl -X POST http://localhost:5678/webhook/social-broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "10293",
    "child_name": "Sami Ahmed",
    "age": 6,
    "location": "Cairo, Egypt",
    "contact_phone": "+201000000000",
    "case_url": "https://kidnap-children.org/posts/10293",
    "image_url": "https://kidnap-children.org/uploads/posts/10293.jpg"
  }'
```
