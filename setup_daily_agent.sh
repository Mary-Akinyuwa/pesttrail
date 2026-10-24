#!/bin/bash
# ============================================================
# Retired. The data agent now runs on GitHub Actions
# (.github/workflows/data-agent.yml), which commits verified
# changes so the live app redeploys.
#
# A local cron would edit the CSV on this machine only — the
# live app never saw those changes — and it stopped whenever
# the laptop slept or changed. Running both would also make
# the two copies diverge.
#
# This script now only removes the old local cron entries.
# ============================================================

crontab -l 2>/dev/null | grep -v "pesttrail-" | grep -v "data_update_agent.py" | crontab -
echo "Old PestTrail cron entries removed (if any)."
echo ""
echo "Schedules now live in .github/workflows/data-agent.yml:"
echo "  Daily            — new detections"
echo "  Monday           — re-verify the stalest records"
echo "  1st of the month — policy figures"
echo ""
echo "Run one now: GitHub → Actions → PestTrail Data Agent → Run workflow."
