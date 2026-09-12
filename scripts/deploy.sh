#!/usr/bin/env bash
# Deploys the built image to the target environment using kustomize.
# Usage: ./scripts/deploy.sh <dev|uat|prod> <image_tag>
set -euo pipefail

ENVIRONMENT="$1"
IMAGE_TAG="$2"
OVERLAY_DIR="k8s/overlays/${ENVIRONMENT}"

if [ ! -d "$OVERLAY_DIR" ]; then
  echo "Unknown environment: $ENVIRONMENT" >&2
  exit 1
fi

echo ">> Setting image to ${CI_REGISTRY_IMAGE}:${IMAGE_TAG} for ${ENVIRONMENT}"
cd "$OVERLAY_DIR"
kustomize edit set image registry.example.com/enterprise-python-demo="${CI_REGISTRY_IMAGE}:${IMAGE_TAG}"
cd - >/dev/null

echo ">> Applying manifests to ${ENVIRONMENT}"
kubectl apply -k "$OVERLAY_DIR"

echo ">> Waiting for rollout"
kubectl rollout status deployment/enterprise-demo-api -n "enterprise-demo-${ENVIRONMENT}" --timeout=180s

echo ">> Deployed ${IMAGE_TAG} to ${ENVIRONMENT} successfully"
