#!/usr/bin/env python3
"""Send UTF-8 text to an exact iMessage address through macOS Messages."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


APPLE_SCRIPT = r'''
on run argv
    if (count of argv) is not 2 then error "recipient and message are required"
    set recipientAddress to item 1 of argv
    set messageText to item 2 of argv
    tell application "Messages"
        set targetService to first service whose service type = iMessage
        set targetBuddy to buddy recipientAddress of targetService
        send messageText to targetBuddy
    end tell
end run
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a text message through macOS iMessage."
    )
    parser.add_argument(
        "--recipient",
        required=True,
        help="Primary iMessage email address or phone number.",
    )
    parser.add_argument(
        "--fallback-email",
        required=True,
        help="iMessage email used only when the primary address is rejected.",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--message", help="Message text to send.")
    source.add_argument("--message-file", type=Path, help="UTF-8 text file to send.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without contacting Messages.",
    )
    return parser.parse_args()


def read_message(args: argparse.Namespace) -> str:
    if args.message_file is not None:
        return args.message_file.read_text(encoding="utf-8")
    if args.message is not None:
        return args.message
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("provide --message, --message-file, or message text on stdin")


def main() -> int:
    args = parse_args()
    try:
        message = read_message(args)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    recipient = args.recipient.strip()
    fallback_email = args.fallback_email.strip()
    email_ok = "@" in recipient and "." in recipient.rsplit("@", 1)[-1]
    phone_ok = bool(re.fullmatch(r"\+?[0-9][0-9 ()-]{6,20}", recipient))
    fallback_ok = "@" in fallback_email and "." in fallback_email.rsplit("@", 1)[-1]
    if not (email_ok or phone_ok) or not fallback_ok or not message.strip():
        print("input error: valid iMessage address, fallback email, and message are required", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"dry run ok: {len(message)} characters")
        return 0

    def send(address: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["osascript", "-", address, message],
            input=APPLE_SCRIPT,
            text=True,
            check=True,
            capture_output=True,
        )

    try:
        send(recipient)
    except FileNotFoundError:
        print("send error: osascript is unavailable; this skill requires macOS", file=sys.stderr)
        return 3
    except subprocess.CalledProcessError as exc:
        if recipient.casefold() == fallback_email.casefold():
            detail = (exc.stderr or exc.stdout or "Messages rejected the send request").strip()
            print(f"send error: {detail}", file=sys.stderr)
            return 4
        try:
            send(fallback_email)
        except subprocess.CalledProcessError as fallback_exc:
            detail = (
                fallback_exc.stderr
                or fallback_exc.stdout
                or "Messages rejected both iMessage addresses"
            ).strip()
            print(f"send error: {detail}", file=sys.stderr)
            return 4
        print("primary iMessage route unavailable; sent via fallback iMessage email")
        return 0

    print("sent via iMessage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
