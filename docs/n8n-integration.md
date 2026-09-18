# n8n Automation & Webhook Integration

The Job Intelligence Platform natively emits event-driven HTTP webhooks for job matches and system events.

## Webhook Event Payload (`job.match`)

When a scraped job matches a user's preferences with a score >= `min_match_score`, the notification service dispatches a POST request:

```json
{
  "event": "job.match",
  "timestamp": "2026-09-16T18:30:00.000Z",
  "match_score": 87,
  "job": {
    "id": 123,
    "title": "Senior Python Backend Developer",
    "company": "TechCorp Global",
    "location": "Remote (Pakistan / Worldwide)",
    "work_mode": "Remote",
    "employment_type": "Full-time",
    "url": "https://remoteok.com/remote-jobs/123",
    "posted_at": "2026-09-16T12:00:00.000Z"
  },
  "user": {
    "id": 42,
    "email": "user@example.com"
  }
}
```

## n8n Workflow Configuration

1. In your **n8n** instance, create a new workflow and add a **Webhook Trigger** node.
2. Set Http Method to `POST` and Path to `job-events`.
3. Copy the test Webhook URL (e.g. `http://localhost:5678/webhook/job-events`).
4. Set `webhook_url` in the user's notification config via API or Database.
5. Connect n8n nodes to send Telegram notifications, Discord alerts, Slack messages, or write to Google Sheets.
