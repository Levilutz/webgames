#!/usr/bin/env bash
# Set up an ingress certificate secret in a cluster namespace
# Expects env vars set:
#   KUBE_NS - kubernetes namespace to get the secret
#   CRT_FILE - path to ingress cert file
#   KEY_FILE - path to ingress key file
# Expects to be authenticated to a kube cluster

set -e

# Check if env vars set
if [[ -z "${KUBE_NS}" ]]
then
    echo "KUBE_NS env var is not set"
    exit 1
fi
if [[ -z "${CRT_FILE}" ]]
then
    echo "CRT_FILE env var is not set"
    exit 1
fi
if [[ -z "${KEY_FILE}" ]]
then
    echo "KEY_FILE env var is not set"
    exit 1
fi

# Validate connected to kube cluster
kubectl auth can-i get pod

# Create ingress secret
kubectl create namespace "${KUBE_NS}" || true
kubectl delete secret ingress-cert --namespace "${KUBE_NS}" || true
kubectl create secret tls ingress-cert \
    --namespace "${KUBE_NS}" --cert="${CRT_FILE}" --key="${KEY_FILE}"
