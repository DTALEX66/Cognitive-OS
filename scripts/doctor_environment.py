from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REMOTE = 'git@github.com:DTALEX66/Cognitive-OS.git'
EXPECTED_GIT_CONFIG = {
    'core.autocrlf': 'false',
    'core.eol': 'lf',
    'i18n.commitEncoding': 'utf-8',
    'i18n.logOutputEncoding': 'utf-8',
}


def run_git(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', *args],
        cwd=PROJECT_ROOT,
        text=True,
        encoding='utf-8',
        errors='replace',
        capture_output=True,
        check=check,
    )


def get_git_value(key: str) -> str:
    result = run_git('config', '--get', key)
    return result.stdout.strip() if result.returncode == 0 else ''


def set_git_value(key: str, value: str) -> None:
    run_git('config', key, value, check=True)


def check_remote(fix: bool) -> list[str]:
    issues: list[str] = []
    current = run_git('remote', 'get-url', 'origin')
    remote = current.stdout.strip() if current.returncode == 0 else ''
    if remote != EXPECTED_REMOTE:
        issues.append(f'origin remote is {remote or "<missing>"}, expected {EXPECTED_REMOTE}')
        if fix:
            run_git('remote', 'set-url', 'origin', EXPECTED_REMOTE, check=True)
    return issues


def check_git_config(fix: bool) -> list[str]:
    issues: list[str] = []
    for key, expected in EXPECTED_GIT_CONFIG.items():
        actual = get_git_value(key)
        if actual.lower() != expected.lower():
            issues.append(f'{key} is {actual or "<unset>"}, expected {expected}')
            if fix:
                set_git_value(key, expected)
    return issues


def check_stdio() -> list[str]:
    issues: list[str] = []
    for name, stream in [('stdin', sys.stdin), ('stdout', sys.stdout), ('stderr', sys.stderr)]:
        encoding = (getattr(stream, 'encoding', None) or '').lower()
        if 'utf' not in encoding:
            issues.append(f'{name} encoding is {encoding or "<unknown>"}, expected UTF-8')
    return issues


def check_encoding_policy() -> list[str]:
    result = subprocess.run(
        [sys.executable, '-m', 'unittest', 'tests.test_encoding_policy'],
        cwd=PROJECT_ROOT,
        text=True,
        encoding='utf-8',
        errors='replace',
        capture_output=True,
    )
    if result.returncode != 0:
        return ['encoding policy test failed:\n' + result.stdout + result.stderr]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description='Check Cognitive-OS local environment invariants.')
    parser.add_argument('--fix', action='store_true', help='Fix repository-local Git settings and origin remote.')
    parser.add_argument('--check-files', action='store_true', help='Run the UTF-8 repository text audit.')
    args = parser.parse_args()

    issues = []
    issues.extend(check_remote(args.fix))
    issues.extend(check_git_config(args.fix))
    issues.extend(check_stdio())
    if args.check_files:
        issues.extend(check_encoding_policy())

    if args.fix:
        remaining = []
        remaining.extend(check_remote(False))
        remaining.extend(check_git_config(False))
        remaining.extend(check_stdio())
        issues = remaining

    if issues:
        print('Environment issues:')
        for issue in issues:
            print(f'- {issue}')
        print('\nPowerShell UTF-8 session setup:')
        print(r'.\scripts\setup_env.ps1')
        return 1

    print('Environment OK: SSH remote, LF line endings, UTF-8 Git settings, and UTF-8 stdio.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
