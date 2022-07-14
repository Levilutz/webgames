#!/usr/bin/env bash
# Set up an external-dns instance in a cluster
# Expects env vars set:
#   DOMAIN - domain in cloudflare to attach to. E.g. "example.com"
#   ZONE_ID - cloudflare zone id of the above domain (32 char hex string).
#   CF_API_TOK - cloudflare api token.
# Expects to be authenticated to a kube cluster
# Expects to be run from repository root

set -e

# Check if env vars set
if [[ -z "${DOMAIN}" ]]
then
    echo "DOMAIN env var is not set"
    exit 1
fi
if [[ -z "${ZONE_ID}" ]]
then
    echo "ZONE_ID env var is not set"
    exit 1
fi
if [[ -z "${CF_API_TOK}" ]]
then
    echo "CF_API_TOK env var is not set"
    exit 1
fi

# Validate connected to kube cluster
kubectl auth can-i get pod

# Add and update helm repo (don't whine if already added)
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns || true
helm repo update

# Create cloudflare key secret
kubectl create namespace external-dns || true
kubectl delete secret cloudflare-token --namespace external-dns || true
kubectl create secret generic cloudflare-token \
    --namespace external-dns --from-literal="token=$CF_API_TOK"

# Install external-dns
helm upgrade --install external-dns external-dns/external-dns \
    --namespace external-dns --create-namespace \
    --set "domainFilters={$DOMAIN}" \
    --set "extraArgs={--cloudflare-proxied, --zone-id-filter=$ZONE_ID}" \
    --values scripts/cluster-init/external-dns-values.yaml
