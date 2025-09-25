#!/bin/bash

# Kubernetes Undeploy Script for BT-API Monorepo
# Usage: ./undeploy.sh

set -e

NAMESPACE="bt-api"

echo "🗑️ Undeploying BT-API from Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Delete all resources
echo "🗑️ Deleting resources..."

# Delete Ingress
kubectl delete -f ../manifests/ingress.yaml --ignore-not-found=true

# Delete Deployments and Services
kubectl delete -f ../manifests/payment-deployment.yaml --ignore-not-found=true
kubectl delete -f ../manifests/dynamic-deployment.yaml --ignore-not-found=true
kubectl delete -f ../manifests/admin-deployment.yaml --ignore-not-found=true
kubectl delete -f ../manifests/hello-deployment.yaml --ignore-not-found=true
kubectl delete -f ../manifests/health-deployment.yaml --ignore-not-found=true

# Delete ConfigMap
kubectl delete -f ../manifests/configmap.yaml --ignore-not-found=true

# Delete Namespace (this will delete all resources in the namespace)
kubectl delete namespace ${NAMESPACE} --ignore-not-found=true

echo "✅ BT-API undeployed successfully!"
