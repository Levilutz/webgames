#!/usr/bin/env bash
# Set up a sendgrid api key secret in a cluster namespace
# Expects env vars set:
#   KUBE_NS - kubernetes namespace to get the secret
#   SENDGRID_KEY - sendgrid api key
# Expects to be authenticated to a kube cluster

set -e

# Check if env vars set
if [[ -z "${KUBE_NS}" ]]
then
    echo "KUBE_NS env var is not set"
    exit 1
fi
if [[ -z "${SENDGRID_KEY}" ]]
then
    echo "SENDGRID_KEY env var is not set"
    exit 1
fi

# Validate connected to kube cluster
kubectl auth can-i get pod

# Create sendgrid secret
kubectl create namespace "${KUBE_NS}" || true
kubectl delete secret sendgrid --namespace "${KUBE_NS}" || true
kubectl create secret generic sendgrid \
    --namespace "${KUBE_NS}" --from-literal="sendgridKey=${SENDGRID_KEY}"
