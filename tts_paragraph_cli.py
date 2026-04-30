#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path

from knj_parser import ParserConfig, build_or_load_manifest

def generate_wav(tts_url: str, paragraph: str, language: str, output_path: Path) -> None:
    payload = json.dumps(
        {"text": paragraph, "language": language}, ensure_ascii=False
    ).encode("utf-8")
    req = urllib.request.Request(
        tts_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    output_path.write_bytes(data)


def print_paragraph(index: int, total: int, paragraph: str, width: int) -> None:
    print(f"\n[{index + 1}/{total}]\n")
    print(textwrap.fill(paragraph, width=width))


def play_wav(path: Path) -> bool:
    if not path.exists():
        print(f"missing audio file: {path}")
        return False

    player = shutil.which("afplay") or shutil.which("ffplay") or shutil.which("aplay")
    if not player:
        print("no audio player found (tried afplay, ffplay, aplay)")
        return False

    cmd = [player, str(path)]
    if player.endswith("ffplay"):
        cmd = [player, "-nodisp", "-autoexit", "-loglevel", "error", str(path)]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"audio playback failed: {exc}")
        return False
    return True


def audio_path(prefix: str, index: int) -> Path:
    return Path(f"{prefix}{index:03d}.wav")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Iterate book paragraphs and generate TTS WAV files."
    )
    parser.add_argument("source", type=Path, help="Source text file path")
    parser.add_argument("--url", default="http://localhost:9999/v1/tts", help="TTS endpoint URL")
    parser.add_argument("--language", default="french", help="Language sent to TTS server")
    parser.add_argument("--out-prefix", default="out", help="Output WAV file prefix")
    parser.add_argument("--start", type=int, default=1, help="1-based paragraph start index")
    parser.add_argument("--width", type=int, default=96, help="Display width")
    parser.add_argument("--rebuild-manifest", action="store_true", help="Rebuild block manifest for this source")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"error: source not found: {args.source}", file=sys.stderr)
        return 1

    if args.rebuild_manifest:
        manifest_path = args.source.with_suffix(".blocks.json")
        if manifest_path.exists():
            manifest_path.unlink()

    manifest = build_or_load_manifest(args.source, config=ParserConfig())
    paragraphs = [block.text for block in manifest.blocks]
    if not paragraphs:
        print("error: no paragraphs found after cleanup", file=sys.stderr)
        return 1

    idx = max(0, min(len(paragraphs) - 1, args.start - 1))

    print("Commands: next|n, prev|p, gen|g, gg, read|r, rr, goto <n>, show|s, quit|q")
    print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)

    while True:
        try:
            cmd = input("\ncmd> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return 0

        if cmd in {"", "n", "next"}:
            idx = min(idx + 1, len(paragraphs) - 1)
            print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)
            continue
        if cmd in {"p", "prev"}:
            idx = max(idx - 1, 0)
            print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)
            continue
        if cmd in {"s", "show"}:
            print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)
            continue
        if cmd.startswith("goto "):
            try:
                target = int(cmd.split(maxsplit=1)[1])
            except ValueError:
                print("invalid index")
                continue
            idx = max(0, min(len(paragraphs) - 1, target - 1))
            print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)
            continue
        if cmd in {"g", "gen", "generate"}:
            output = audio_path(args.out_prefix, idx + 1)
            try:
                generate_wav(args.url, paragraphs[idx], args.language, output)
            except urllib.error.URLError as exc:
                print(f"tts request failed: {exc}")
                continue
            except TimeoutError:
                print("tts request timed out")
                continue
            print(f"saved {output}")
            continue
        if cmd in {"r", "read"}:
            output = audio_path(args.out_prefix, idx + 1)
            if play_wav(output):
                print(f"played {output}")
            continue
        if cmd == "rr":
            try:
                while idx < len(paragraphs):
                    output = audio_path(args.out_prefix, idx + 1)
                    if not output.exists():
                        print(f"stopped at missing audio file: {output}")
                        break
                    print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)
                    if not play_wav(output):
                        print(f"stopped due to playback failure: {output}")
                        break
                    print(f"played {output}")
                    if idx == len(paragraphs) - 1:
                        print("reached last paragraph")
                        break
                    idx += 1
            except KeyboardInterrupt:
                print("\ninterrupted rr")
            continue
        if cmd == "gg":
            try:
                while idx < len(paragraphs):
                    output = audio_path(args.out_prefix, idx + 1)
                    print_paragraph(idx, len(paragraphs), paragraphs[idx], args.width)
                    if output.exists():
                        print(f"exists {output} (skip)")
                    else:
                        try:
                            generate_wav(args.url, paragraphs[idx], args.language, output)
                        except urllib.error.URLError as exc:
                            print(f"tts request failed: {exc}")
                            break
                        except TimeoutError:
                            print("tts request timed out")
                            break
                        print(f"saved {output}")
                    if idx == len(paragraphs) - 1:
                        print("reached last paragraph")
                        break
                    idx += 1
            except KeyboardInterrupt:
                print("\ninterrupted gg")
            continue
        if cmd in {"q", "quit", "exit"}:
            print("bye")
            return 0

        print("unknown command; use next, prev, gen, gg, read, rr, goto <n>, show, quit")


if __name__ == "__main__":
    raise SystemExit(main())
