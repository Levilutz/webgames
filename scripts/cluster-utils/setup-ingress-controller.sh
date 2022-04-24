#!/usr/bin/env bash
# Set up an nginx ingress controller in a cluster
# Allows env vars set (if you want to install/upgrade tls secret):
#   TLS_CRT_FILE - path to the TLS cert file
#   TLS_KEY_FILE - path to the TLS key file
# Expects to be authenticated to a kube cluster

set -e

# Validate connected to kube cluster
kubectl auth can-i get pod

# Add and update helm repo (don't whine if already added)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx || true
helm repo update

# Install ingress-nginx (the community one)
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx --create-namespace \
    --set "controller.ingressClassResource.default=true"

# Check if env vars set, exit quietly if not
if [[ -z "${TLS_CRT_FILE}" ]]
then
    echo "TLS_CRT_FILE env var is not set - not installing tls secret"
    exit 0
fi
if [[ -z "${TLS_KEY_FILE}" ]]
then
    echo "TLS_KEY_FILE env var is not set - not installing tls secret"
    exit 0
fi

# Check that files exist (before potentially deleting existing secret)
if [[ ! -f "${TLS_CRT_FILE}" ]]
then
    echo "TLS_CRT_FILE ${TLS_CRT_FILE} not found"
    exit 1
fi
if [[ ! -f "${TLS_KEY_FILE}" ]]
then
    echo "TLS_KEY_FILE ${TLS_KEY_FILE} not found"
    exit 1
fi

# Create origin cert secret
kubectl delete secret ingress-cert || true
kubectl create secret tls ingress-cert --cert="$TLS_CRT_FILE" --key="$TLS_KEY_FILE"
