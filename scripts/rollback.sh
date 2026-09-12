#!/usr/bin/env bash
# Rolls the given environment back to the previous successful deployment.
# Usage: ./scripts/rollback.sh <dev|uat|prod>
set -euo pipefail

ENVIRONMENT="$1"
NAMESPACE="enterprise-demo-${ENVIRONMENT}"

echo ">> Rolling back deployment in ${NAMESPACE}"
kubectl rollout undo deployment/enterprise-demo-api -n "$NAMESPACE"
kubectl rollout status deployment/enterprise-demo-api -n "$NAMESPACE" --timeout=180s

echo ">> Rollback complete for ${ENVIRONMENT}"
kubectl get deployment enterprise-demo-api -n "$NAMESPACE" -o \
  jsonpath='{.spec.template.spec.containers[0].image}'
