#!/usr/bin/env bash
# Sends a deployment/pipeline notification to Slack/Teams via an incoming
# webhook stored as a masked CI/CD variable (SLACK_WEBHOOK_URL / TEAMS_WEBHOOK_URL).
set -euo pipefail

STATUS="$1"          # success | failure
ENVIRONMENT="$2"      # dev | uat | prod
MESSAGE="Pipeline *${CI_PIPELINE_ID:-local}* for *${CI_PROJECT_NAME:-app}* \
(commit ${CI_COMMIT_SHORT_SHA:-local}) -> ${ENVIRONMENT}: ${STATUS}"

if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
  curl -s -X POST -H 'Content-type: application/json' \
    --data "{\"text\": \"${MESSAGE}\"}" \
    "$SLACK_WEBHOOK_URL" >/dev/null || echo "Slack notification failed (non-blocking)"
else
  echo "SLACK_WEBHOOK_URL not set, skipping Slack notification"
  echo "$MESSAGE"
fi
