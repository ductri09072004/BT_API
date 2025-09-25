#!/bin/bash

# Check Status of BT-API in Kubernetes
# Usage: ./status.sh

set -e

NAMESPACE="bt-api"

echo "📊 BT-API Status in Kubernetes"
echo "================================"

# Check namespace
echo "📦 Namespace:"
kubectl get namespace ${NAMESPACE} 2>/dev/null || echo "❌ Namespace not found"

echo ""

# Check pods
echo "🔄 Pods:"
kubectl get pods -n ${NAMESPACE} -o wide

echo ""

# Check services
echo "🌐 Services:"
kubectl get services -n ${NAMESPACE}

echo ""

# Check ingress
echo "🚪 Ingress:"
kubectl get ingress -n ${NAMESPACE}

echo ""

# Check deployments
echo "🚀 Deployments:"
kubectl get deployments -n ${NAMESPACE}

echo ""

# Check PVCs
echo "💾 Persistent Volume Claims:"
kubectl get pvc -n ${NAMESPACE}

echo ""

# Show logs for each service
echo "📋 Recent Logs:"
echo "==============="

services=("health-service" "hello-service" "admin-service" "dynamic-service" "payment-service")

for service in "${services[@]}"; do
    echo ""
    echo "📝 ${service} logs:"
    kubectl logs -n ${NAMESPACE} -l app=${service} --tail=5 2>/dev/null || echo "No logs available"
done

echo ""
echo "🔍 To get more detailed information:"
echo "  kubectl describe pods -n ${NAMESPACE}"
echo "  kubectl logs -n ${NAMESPACE} -l app=<service-name>"
echo "  kubectl get events -n ${NAMESPACE}"
