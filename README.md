# iMessage Delivery by Wayne

Send text, images, PDFs, and documents from a Mac to an iPhone through Apple Messages, with an explicit guard against accidentally falling back to SMS/MMS.

This skill is useful for Codex users who want scheduled reports, reminders, daily summaries, chart images, or generated documents delivered to their iPhone from a Mac that is already signed in to Messages.

## What It Does

- Sends text through the macOS Messages iMessage service.
- Sends images, PDFs, and documents through the Messages UI by pasting the file into the message input field.
- Requires an explicit iMessage route check before sending attachments.
- Verifies that an attachment is staged before pressing Return.
- Keeps SMS/MMS fallback out of the happy path, because attachment delivery over carrier messaging can be expensive.

## Requirements

- macOS with the Messages app signed in.
- The recipient must be reachable through iMessage.
- AppleScript/System Events accessibility permissions may be required.
- Python 3.
- For attachment sending, the target Messages conversation should already be open or selectable, and the input placeholder must explicitly indicate iMessage.

## Installation

Clone or download this repository, then copy the repository folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/imessage-delivery-by-wayne ~/.codex/skills/imessage-delivery
```

Restart Codex if needed so the skill list refreshes.

## Sending Text

Use `send_imessage.py` for text-only messages:

```bash
python3 ~/.codex/skills/imessage-delivery/scripts/send_imessage.py \
  --recipient '+15551234567' \
  --fallback-email 'user@example.icloud.com' \
  --message 'Hello from Codex'
```

For longer reports, prefer a UTF-8 text file:

```bash
python3 ~/.codex/skills/imessage-delivery/scripts/send_imessage.py \
  --recipient '+15551234567' \
  --fallback-email 'user@example.icloud.com' \
  --message-file '/absolute/path/to/report.txt'
```

The script uses the AppleScript service whose type is `iMessage`. If the primary address is rejected, it retries with the fallback iMessage email.

## Sending Images, PDFs, Or Documents

Use `send_imessage_attachment.py` for files:

```bash
python3 ~/.codex/skills/imessage-delivery/scripts/send_imessage_attachment.py \
  --chat-title 'Recipient Name' \
  --file '/absolute/path/to/report.jpg' \
  --imessage-route-verified
```

Important: only pass `--imessage-route-verified` after confirming in the Messages UI that the input field placeholder says iMessage, such as `iMessage信息` on a Chinese macOS system. If the route says SMS, MMS, text message, is green, or is unclear, do not send.

## Recommended Attachment Workflow

1. Open the intended Messages conversation.
2. Confirm the conversation title matches the intended recipient.
3. Confirm the message input is an iMessage input, not SMS/MMS.
4. Run the attachment script with `--imessage-route-verified`.
5. Check Messages for the delivered status.

## Dry Run

Both scripts support `--dry-run` for safe validation:

```bash
python3 ~/.codex/skills/imessage-delivery/scripts/send_imessage_attachment.py \
  --chat-title 'Recipient Name' \
  --file '/absolute/path/to/report.jpg' \
  --dry-run
```

## Safety Notes

- Do not include passwords, API keys, private tokens, or unrelated sensitive data in messages.
- Do not send attachments unless the iMessage route is visibly confirmed.
- Treat "sent" and "delivered" as different states; inspect Messages when delivery matters.
- If a phone number is not recognized as iMessage, use a confirmed iMessage email address instead.

## Included Files

```text
imessage-delivery/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    ├── send_imessage.py
    └── send_imessage_attachment.py
```

## License

MIT
