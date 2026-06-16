#!/usr/bin/env bash
set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/com.yonghun.cs-interview-study.plist"

launchctl unload "$PLIST" >/dev/null 2>&1 || true
rm -f "$PLIST"

echo "Disabled daily study note."
