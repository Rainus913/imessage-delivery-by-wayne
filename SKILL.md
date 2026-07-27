---
name: imessage-delivery
description: Send reports, reminders, summaries, images, PDFs, documents, or other user-approved content from a Mac to an iPhone through Apple Messages, preferring a phone number when it is registered for iMessage and falling back to an iMessage email instead of SMS. Use when the user asks to send something by Mac Messages, iMessage, or to their iPhone, or when a recurring automation must deliver its result through iMessage.
---

# iMessage Delivery

Send text or files through the Mac Messages app while guaranteeing iMessage delivery routing. A phone number is acceptable when it uses iMessage; never silently downgrade to SMS.

## Workflow

1. Finish and review the message before opening the send path. Do not include API keys, passwords, or unrelated sensitive data.
2. If the user supplies or selects a phone number, check whether Messages identifies the route as iMessage. A blue/iMessage route is valid. If the route is green, SMS, or uncertain, use a user-approved iMessage email address instead.
3. For an ad hoc message, show the recipient and a short description of the content, then obtain explicit confirmation immediately before sending. Treat a user-created recurring automation that names both the content and destination as standing authorization for its scheduled runs.
4. Choose the send path by content type:
   - Text-only content: use `scripts/send_imessage.py`. Prefer `--message-file` for long reports and `--message` for short text.
   - Images, PDFs, or documents: use `scripts/send_imessage_attachment.py`. This uses the reliable UI path: copy the file to the clipboard, paste it into the selected iMessage input field, verify an attachment object is staged, press Return, and verify `已送达`.

```bash
python3 ~/.codex/skills/imessage-delivery/scripts/send_imessage.py \
  --recipient '+15551234567' \
  --fallback-email 'user@example.icloud.com' \
  --message 'Message text'
```

```bash
python3 ~/.codex/skills/imessage-delivery/scripts/send_imessage_attachment.py \
  --chat-title 'Recipient Name' \
  --file '/absolute/path/to/report.jpg' \
  --imessage-route-verified
```

5. Text sending uses only the AppleScript service whose type is `iMessage`; it never invokes an SMS service. If the primary phone address is not accepted by iMessage, it retries once through the fallback email. For manual UI sending, inspect the route before sending and switch to the email if it indicates SMS.
6. File sending requires the Messages UI to already contain or be able to open the exact iMessage conversation named by `--chat-title`. Before sending, use Computer Use or another UI inspection path to verify all of the following:
   - The front Messages window title matches the intended conversation.
   - The message input `Help` matches the intended recipient.
   - The message input placeholder is exactly `iMessage信息`, or an equivalent locale string that explicitly says iMessage. If it says SMS, MMS, text message, is green, or is missing/uncertain, stop and do not send.
   - Only after this check, pass `--imessage-route-verified` to the attachment script.
7. After sending, report success only if the script exits successfully. When delivery confirmation matters and the Messages UI is available, inspect the conversation and verify `已送达` or the equivalent delivered status. Distinguish “sent” from “delivered”.

## Recurring Reports

For scheduled training reports or reminders:

- Generate the report first from the authorized source.
- Send only the finished report, never credentials or raw API responses.
- If generation fails or required data is unavailable, send a short honest status rather than inventing content.
- Keep the scheduled destination fixed to a user-approved iMessage address. A phone may be primary only when verified as iMessage; configure the email fallback so scheduled runs never downgrade to SMS.

## Script

`scripts/send_imessage.py` launches the existing Mac Messages app through AppleScript. It accepts an email or phone as the primary iMessage address, retries through a fallback email when the primary iMessage route fails, preserves UTF-8 line breaks, supports a message file, and provides `--dry-run` for validation without sending.

`scripts/send_imessage_attachment.py` sends an image, PDF, or document through the Messages UI path that has been verified for picture delivery. It accepts an exact chat title plus a local file path, requires the caller to assert `--imessage-route-verified` after UI inspection, stages the file in the iMessage input field, confirms the staged attachment object exists, sends it, and checks the transcript for a delivered status.
