#!/usr/bin/env python3
"""Send a local file through the currently available macOS Messages UI."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send an image, PDF, or document through a verified iMessage chat."
    )
    parser.add_argument(
        "--chat-title",
        required=True,
        help="Exact Messages conversation title, for example 'Recipient Name'.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Local file path to send.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without touching Messages.",
    )
    parser.add_argument(
        "--imessage-route-verified",
        action="store_true",
        help=(
            "Required for real sends. Use only after UI inspection confirms the "
            "message input placeholder explicitly says iMessage."
        ),
    )
    return parser.parse_args()


def run_osascript(*lines: str) -> subprocess.CompletedProcess[str]:
    cmd: list[str] = ["osascript"]
    for line in lines:
        cmd.extend(["-e", line])
    return subprocess.run(cmd, text=True, check=True, capture_output=True)


def copy_file_to_clipboard(path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        run_osascript(
            f'set imagePath to POSIX file "{path}"',
            "set the clipboard to (read imagePath as JPEG picture)",
        )
        return
    if suffix == ".png":
        run_osascript(
            f'set imagePath to POSIX file "{path}"',
            "set the clipboard to (read imagePath as PNG picture)",
        )
        return
    run_osascript(
        f'set filePath to POSIX file "{path}"',
        "set the clipboard to filePath",
    )


def get_messages_state() -> str:
    script = r'''
tell application "Messages" to activate
delay 0.2
tell application "System Events"
    tell process "Messages"
        set windowTitle to name of front window
        set fieldInfo to ""
        try
            set messageField to first text area of front window whose subrole is "AXTextArea"
            set fieldValue to value of messageField as text
            set fieldInfo to fieldValue
        end try
        return windowTitle & linefeed & fieldInfo
    end tell
end tell
'''
    return subprocess.run(
        ["osascript", "-"],
        input=script,
        text=True,
        check=True,
        capture_output=True,
    ).stdout


def main() -> int:
    args = parse_args()
    file_path = args.file.expanduser().resolve()
    if not file_path.is_file():
        print(f"input error: file does not exist: {file_path}", file=sys.stderr)
        return 2
    if not args.chat_title.strip():
        print("input error: --chat-title is required", file=sys.stderr)
        return 2
    if not args.dry_run and not args.imessage_route_verified:
        print(
            "input error: confirm the Messages input says iMessage, then pass "
            "--imessage-route-verified",
            file=sys.stderr,
        )
        return 2
    if args.dry_run:
        print(f"dry run ok: {file_path}")
        return 0

    try:
        copy_file_to_clipboard(file_path)
        run_osascript(f'tell application "Messages" to activate')
        time.sleep(0.5)
        state_before = get_messages_state()
        if args.chat_title not in state_before.splitlines()[0]:
            print(
                f"send error: front Messages window is not the expected chat '{args.chat_title}'",
                file=sys.stderr,
            )
            return 4
        run_osascript('tell application "System Events" to keystroke "v" using command down')
        time.sleep(1.2)
        state_after_paste = get_messages_state()
        if "\ufffc" not in state_after_paste:
            print("send error: attachment was not staged in the message field", file=sys.stderr)
            return 4
        run_osascript('tell application "System Events" to key code 36')
        time.sleep(2.0)
        print("sent attachment via Messages UI; inspect Messages for delivered status")
        return 0
    except FileNotFoundError:
        print("send error: osascript is unavailable; this skill requires macOS", file=sys.stderr)
        return 3
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "Messages rejected the UI send request").strip()
        print(f"send error: {detail}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
