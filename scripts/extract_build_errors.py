#!/usr/bin/env python3
"""
scripts/extract_build_errors.py
Extracts exact compiler, linker, AAPT2, and Ninja errors from Android/LineageOS build logs.
Formats them cleanly for GitHub Actions workflow logs, annotations, and Step Summaries.
"""

import os
import re
import sys

def parse_log(log_path):
    if not os.path.exists(log_path):
        return [], []

    failed_blocks = []
    current_block = []
    recording = False

    failed_re = re.compile(r'^FAILED:\s*(.*)')
    progress_re = re.compile(r'^\[\s*\d+%\s+\d+/\d+\]')
    ninja_stopped_re = re.compile(r'^ninja:\s*build stopped:\s*(.*)')
    make_err_re = re.compile(r'^make(?:\[\d+\])?: \*\*\* (.*)')
    oom_re = re.compile(r'(out of memory|internal compiler error: Killed|fatal error: unable to execute command: Killed)', re.IGNORECASE)
    disk_re = re.compile(r'No space left on device', re.IGNORECASE)

    general_diagnostics = []

    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_str = line.rstrip()
            
            # Start of a Ninja FAILED block
            m_failed = failed_re.match(line_str)
            if m_failed:
                if current_block:
                    failed_blocks.append('\n'.join(current_block))
                    current_block = []
                recording = True
                current_block.append(line_str)
                continue

            if recording:
                # Stop recording when next progress indicator or stop marker is hit
                if progress_re.match(line_str) or ninja_stopped_re.match(line_str) or make_err_re.match(line_str):
                    recording = False
                    failed_blocks.append('\n'.join(current_block))
                    current_block = []
                    if ninja_stopped_re.match(line_str) or make_err_re.match(line_str):
                        general_diagnostics.append(line_str)
                else:
                    current_block.append(line_str)
            else:
                if ninja_stopped_re.match(line_str) or make_err_re.match(line_str):
                    general_diagnostics.append(line_str)
                elif oom_re.search(line_str):
                    general_diagnostics.append(f"OOM: {line_str}")
                elif disk_re.search(line_str):
                    general_diagnostics.append(f"DISK FULL: {line_str}")

        if current_block:
            failed_blocks.append('\n'.join(current_block))

    return failed_blocks, general_diagnostics

def extract_file_and_line(block_text):
    """Attempt to extract file and line number from compiler diagnostic for GitHub annotation."""
    # Pattern: path/to/file.cpp:123:45: error: ...
    m = re.search(r'([a-zA-Z0-9_\-\./]+\.(?:cpp|c|h|hpp|java|kt|aidl|xml|mk|bp)):(\d+):(?:\d+:)?\s*(error:.*)', block_text)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None, None, None

def main():
    build_log = sys.argv[1] if len(sys.argv) > 1 else "build.log"
    soong_error_log = sys.argv[2] if len(sys.argv) > 2 else ""

    print("\n" + "=" * 70)
    print(">>> RUNNING AUTOMATED BUILD ERROR EXTRACTION & ROOT-CAUSE ANALYSIS")
    print("=" * 70)

    failed_blocks, general_diagnostics = parse_log(build_log)

    # Also inspect out/error.log if it exists and has content
    soong_errors = []
    if soong_error_log and os.path.exists(soong_error_log):
        with open(soong_error_log, 'r', encoding='utf-8', errors='ignore') as f:
            soong_errors = [l.strip() for l in f if l.strip()]

    summary_lines = []
    summary_lines.append("## ❌ LineageOS Build Failure Diagnostics\n")

    if failed_blocks:
        print(f"\n[!] Detected {len(failed_blocks)} failed task(s) in Ninja execution:\n")
        summary_lines.append(f"**Found {len(failed_blocks)} failed task(s) during compilation:**\n")

        for idx, block in enumerate(failed_blocks):
            print(f"--- FAILURE #{idx + 1} ---")
            print(block)
            print("-" * 50)

            # Emit GitHub annotation if possible
            filepath, lineno, errmsg = extract_file_and_line(block)
            if filepath and lineno:
                print(f"::error file={filepath},line={lineno}::{errmsg}")

            summary_lines.append(f"### Failure #{idx + 1}")
            summary_lines.append("```text")
            # Truncate block to reasonable size for step summary (max 40 lines per block)
            block_lines = block.splitlines()
            if len(block_lines) > 40:
                summary_lines.extend(block_lines[:35])
                summary_lines.append(f"... ({len(block_lines) - 35} lines omitted) ...")
                summary_lines.extend(block_lines[-5:])
            else:
                summary_lines.extend(block_lines)
            summary_lines.append("```\n")
    else:
        print("\n[-] No explicit 'FAILED:' target blocks matched in build.log.")

    if general_diagnostics:
        print("\n[!] General build diagnostics:")
        summary_lines.append("### Diagnostic Markers\n```text")
        for diag in general_diagnostics:
            print(f"  * {diag}")
            summary_lines.append(diag)
        summary_lines.append("```\n")

    if soong_errors:
        print("\n[!] Errors reported by Soong (out/error.log):")
        summary_lines.append("### Soong Error Log\n```text")
        for err in soong_errors[:30]:
            print(f"  * {err}")
            summary_lines.append(err)
        summary_lines.append("```\n")

    # If no structured errors were found, dump the last 60 lines of the build log
    if not failed_blocks and not general_diagnostics and not soong_errors:
        print("\n[!] Extracting trailing 60 lines of build log for triage:")
        if os.path.exists(build_log):
            with open(build_log, 'r', encoding='utf-8', errors='ignore') as f:
                trailing = f.readlines()[-60:]
            for l in trailing:
                sys.stdout.write(l)
            summary_lines.append("### Trailing Log Output\n```text")
            summary_lines.extend([l.rstrip() for l in trailing[-40:]])
            summary_lines.append("```\n")

    # Write to GitHub Step Summary if running in GitHub Actions
    step_summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if step_summary_file:
        try:
            with open(step_summary_file, 'a', encoding='utf-8') as f:
                f.write('\n'.join(summary_lines) + '\n')
            print(f"\n[+] Wrote formatted diagnostic report to GITHUB_STEP_SUMMARY.")
        except Exception as e:
            print(f"[-] Failed writing to GITHUB_STEP_SUMMARY: {e}")

    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
