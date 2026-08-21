---
name: imessage-delivery
description: Send user-approved text or files from a Mac to an iPhone through Apple Messages, preferring the Messages plugin and falling back to verified iMessage-only scripts. Use when the user asks to send something by Mac Messages, iMessage, or to their iPhone, or when a recurring automation must deliver its result through iMessage.
---

# iMessage Delivery

Send text or files through the Mac Messages app while preserving iMessage-only routing. Prefer the Messages plugin for ordinary sends. Use the bundled scripts only when the plugin is unavailable, fails, or delivery-status verification is required. A phone number is acceptable only when its route is known to be iMessage; never silently downgrade to SMS.

## Workflow

1. Finish and review the message before opening the send path. Do not include API keys, passwords, or unrelated sensitive data.
2. Resolve the destination before sending:
   - Prefer an existing exact chat returned by the Messages plugin's `find_chats` and reuse its stable `chat_guid`.
   - Accept the chat only when its service is explicitly iMessage and its participants match the intended recipient. Do not rely on a display name alone when multiple chats match.
   - If the user supplies a phone number and its route is SMS, green, or uncertain, use a user-approved iMessage email instead. If neither route can be verified as iMessage, stop.
3. For an ad hoc send, show the resolved recipient or chat and a short description of the text and attachments, then obtain explicit confirmation immediately before sending. Treat a user-created recurring automation that fixes both the content and destination as standing authorization for its scheduled runs.
4. Prefer the Messages plugin's `send_message` for text, local file attachments, or both:
   - Use the verified `chat_guid` when available; otherwise use only an approved iMessage recipient address.
   - Pass absolute paths for attachments and include only the files the user approved.
   - If the user edits the message in the plugin's approval step, treat the edited version as authoritative.
   - Report plugin success as sent or accepted for sending. Do not claim `已送达` unless delivery was separately verified.
5. Fall back to the bundled scripts only when the Messages plugin is unavailable, its send fails, or the user requires delivery confirmation:
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

6. Script-based text sending uses only the AppleScript service whose type is `iMessage`; it never invokes an SMS service. If the primary phone address is not accepted by iMessage, it retries once through the fallback email. For manual UI sending, inspect the route before sending and switch to the email if it indicates SMS.
7. Script-based file sending requires the Messages UI to already contain or be able to open the exact iMessage conversation named by `--chat-title`. Before sending, use Computer Use or another UI inspection path to verify all of the following:
   - The front Messages window title matches the intended conversation.
   - The message input `Help` matches the intended recipient.
   - The message input placeholder is exactly `iMessage信息`, or an equivalent locale string that explicitly says iMessage. If it says SMS, MMS, text message, is green, or is missing/uncertain, stop and do not send.
   - Only after this check, pass `--imessage-route-verified` to the attachment script.
8. After sending, report which path was used. For a script fallback, report success only if the script exits successfully. When delivery confirmation matters and the Messages UI is available, inspect the conversation and verify `已送达` or the equivalent delivered status. Always distinguish “sent” from “delivered”.

## Recurring Reports

For scheduled training reports or reminders:

- Generate the report first from the authorized source.
- Send only the finished report, never credentials or raw API responses.
- If generation fails or required data is unavailable, send a short honest status rather than inventing content.
- Keep the scheduled destination fixed to a user-approved iMessage `chat_guid` or address. A phone may be primary only when verified as iMessage; retain the approved email fallback so scheduled runs never downgrade to SMS.
- Prefer the Messages plugin for scheduled delivery when it is available. If it is unavailable or fails, use the matching bundled script once; do not repeatedly retry an external send.

## Script

`scripts/send_imessage.py` launches the existing Mac Messages app through AppleScript. It accepts an email or phone as the primary iMessage address, retries through a fallback email when the primary iMessage route fails, preserves UTF-8 line breaks, supports a message file, and provides `--dry-run` for validation without sending.

`scripts/send_imessage_attachment.py` sends an image, PDF, or document through the Messages UI path that has been verified for picture delivery. It accepts an exact chat title plus a local file path, requires the caller to assert `--imessage-route-verified` after UI inspection, stages the file in the iMessage input field, confirms the staged attachment object exists, sends it, and checks the transcript for a delivered status.
