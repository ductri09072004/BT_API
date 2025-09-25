#!/bin/bash

# Build and Push Docker Images for Kubernetes
# Usage: ./build-and-push.sh [registry] [tag]

set -e

REGISTRY=${1:-localhost:5000}
TAG=${2:-latest}

echo "🐳 Building and pushing Docker images..."
echo "Registry: ${REGISTRY}"
echo "Tag: ${TAG}"

# Build images
echo "🔨 Building Docker images..."

# Health service
echo "  🏥 Building health service..."
docker build -t ${REGISTRY}/bt_api-health:${TAG} ../services/health/
docker push ${REGISTRY}/bt_api-health:${TAG}

# Hello service
echo "  👋 Building hello service..."
docker build -t ${REGISTRY}/bt_api-hello:${TAG} ../services/hello/
docker push ${REGISTRY}/bt_api-hello:${TAG}

# Admin service
echo "  ⚙️ Building admin service..."
docker build -t ${REGISTRY}/bt_api-admin:${TAG} ../services/admin/
docker push ${REGISTRY}/bt_api-admin:${TAG}

# Dynamic service
echo "  🔄 Building dynamic service..."
docker build -t ${REGISTRY}/bt_api-dynamic:${TAG} ../services/dynamic/
docker push ${REGISTRY}/bt_api-dynamic:${TAG}

# Payment service
echo "  💳 Building payment service..."
docker build -t ${REGISTRY}/bt_api-payment:${TAG} ../services/payment/
docker push ${REGISTRY}/bt_api-payment:${TAG}

echo "✅ All images built and pushed successfully!"

# Update image references in manifests
echo "📝 Updating image references in manifests..."

# Update all deployment files
find ../manifests -name "*-deployment.yaml" -exec sed -i "s|image: bt_api-|image: ${REGISTRY}/bt_api-|g" {} \;

echo "✅ Image references updated!"
