#!/bin/bash

# Kubernetes Deployment Script for BT-API Monorepo
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-dev}
NAMESPACE="bt-api"

echo "🚀 Deploying BT-API to Kubernetes (${ENVIRONMENT})..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f ../manifests/namespace.yaml

# Apply ConfigMap
echo "⚙️ Applying ConfigMap..."
kubectl apply -f ../manifests/configmap.yaml

# Deploy services
echo "🔧 Deploying services..."

# Health service
echo "  🏥 Deploying health service..."
kubectl apply -f ../manifests/health-deployment.yaml

# Hello service
echo "  👋 Deploying hello service..."
kubectl apply -f ../manifests/hello-deployment.yaml

# Admin service
echo "  ⚙️ Deploying admin service..."
kubectl apply -f ../manifests/admin-deployment.yaml

# Dynamic service
echo "  🔄 Deploying dynamic service..."
kubectl apply -f ../manifests/dynamic-deployment.yaml

# Payment service
echo "  💳 Deploying payment service..."
kubectl apply -f ../manifests/payment-deployment.yaml

# Apply Ingress
echo "🌐 Applying Ingress..."
kubectl apply -f ../manifests/ingress.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/health-service -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=300s deployment/hello-service -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=300s deployment/admin-service -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=300s deployment/dynamic-service -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=300s deployment/payment-service -n ${NAMESPACE}

echo "✅ All services deployed successfully!"

# Show status
echo "📊 Deployment Status:"
kubectl get pods -n ${NAMESPACE}
kubectl get services -n ${NAMESPACE}
kubectl get ingress -n ${NAMESPACE}

echo ""
echo "🌐 Access URLs:"
echo "  Health: http://health.bt-api.local/healthz"
echo "  Hello:  http://hello.bt-api.local/A"
echo "  Admin:  http://admin.bt-api.local/admin/routes"
echo "  Dynamic: http://dynamic.bt-api.local/{path}"
echo "  Payment: http://payment.bt-api.local/healthz"
echo ""
echo "💡 To access locally, add to /etc/hosts:"
echo "  127.0.0.1 health.bt-api.local hello.bt-api.local admin.bt-api.local dynamic.bt-api.local payment.bt-api.local"
