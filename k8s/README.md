# 🚀 Kubernetes Deployment for BT-API Monorepo

Hướng dẫn deploy các microservices lên Kubernetes cluster.

## 📂 Cấu trúc

```
k8s/
├── manifests/                 # Kubernetes manifests
│   ├── namespace.yaml        # Namespace definition
│   ├── configmap.yaml        # Configuration
│   ├── health-deployment.yaml # Health service
│   ├── hello-deployment.yaml  # Hello service
│   ├── admin-deployment.yaml  # Admin service
│   ├── dynamic-deployment.yaml # Dynamic service
│   ├── payment-deployment.yaml # Payment service
│   └── ingress.yaml          # Ingress configuration
├── scripts/                  # Deployment scripts
│   ├── deploy.sh            # Deploy all services
│   ├── undeploy.sh          # Remove all services
│   ├── build-and-push.sh    # Build and push images
│   └── status.sh            # Check status
├── Makefile                 # Management commands
└── README.md               # This file
```

## 🚀 Quick Start

### 1. **Prerequisites**

```bash
# Install kubectl
# Install Docker
# Have access to a Kubernetes cluster
```

### 2. **Build and Push Images**

```bash
# Build and push to local registry
make build-push

# Or to specific registry
make build-push REGISTRY=myregistry.com TAG=v1.0.0
```

### 3. **Deploy to Kubernetes**

```bash
# Deploy all services
make deploy

# Check status
make status
```

### 4. **Access Services**

```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 health.bt-api.local hello.bt-api.local admin.bt-api.local dynamic.bt-api.local payment.bt-api.local

# Access services
curl http://health.bt-api.local/healthz
curl http://hello.bt-api.local/A
curl http://admin.bt-api.local/admin/routes
```

## 🛠️ Management Commands

### **Deployment**
```bash
make deploy          # Deploy all services
make undeploy        # Remove all services
make status          # Check status
```

### **Docker Images**
```bash
make build-push                    # Build and push images
make build-push REGISTRY=myregistry.com TAG=v1.0.0
```

### **Monitoring**
```bash
make logs                          # Show all logs
make logs SERVICE=payment-service  # Show specific service logs
```

### **Local Testing**
```bash
make port-forward    # Port forward for local testing
```

## 🌐 Services và URLs

| Service | URL | Description |
|---------|-----|-------------|
| Health | `http://health.bt-api.local/healthz` | Health check |
| Hello | `http://hello.bt-api.local/A` | Hello world |
| Admin | `http://admin.bt-api.local/admin/routes` | Admin APIs |
| Dynamic | `http://dynamic.bt-api.local/{path}` | Dynamic routes |
| Payment | `http://payment.bt-api.local/healthz` | Payment service |

## 📊 Kubernetes Resources

### **Deployments**
- **health-service**: 2 replicas
- **hello-service**: 2 replicas  
- **admin-service**: 2 replicas
- **dynamic-service**: 2 replicas
- **payment-service**: 2 replicas

### **Services**
- ClusterIP services for internal communication
- Load balancing across replicas

### **Persistent Storage**
- **admin-data-pvc**: 1Gi storage for admin service
- **dynamic-data-pvc**: 1Gi storage for dynamic service

### **Ingress**
- Path-based routing
- Subdomain-based routing
- SSL termination ready

## 🔧 Configuration

### **Environment Variables**
```yaml
DEBUG: "true"
ENVIRONMENT: "production"
LOG_LEVEL: "info"
```

### **Resource Limits**
```yaml
# Health/Hello services
requests:
  memory: "64Mi"
  cpu: "50m"
limits:
  memory: "128Mi"
  cpu: "100m"

# Admin/Dynamic/Payment services
requests:
  memory: "128Mi"
  cpu: "100m"
limits:
  memory: "256Mi"
  cpu: "200m"
```

## 🚨 Troubleshooting

### **Check Pod Status**
```bash
kubectl get pods -n bt-api
kubectl describe pod <pod-name> -n bt-api
```

### **Check Logs**
```bash
kubectl logs -n bt-api -l app=health-service
kubectl logs -n bt-api -l app=admin-service
```

### **Check Services**
```bash
kubectl get services -n bt-api
kubectl get ingress -n bt-api
```

### **Check Events**
```bash
kubectl get events -n bt-api --sort-by='.lastTimestamp'
```

## 🔄 Scaling

### **Scale Services**
```bash
# Scale specific service
kubectl scale deployment health-service --replicas=3 -n bt-api

# Scale all services
kubectl scale deployment --replicas=3 --all -n bt-api
```

### **Auto Scaling**
```bash
# Enable HPA for a service
kubectl autoscale deployment health-service --cpu-percent=70 --min=2 --max=10 -n bt-api
```

## 🧹 Cleanup

```bash
# Remove all resources
make undeploy

# Or manually
kubectl delete namespace bt-api
```

## 📈 Production Considerations

1. **Use proper image registry** (Docker Hub, ECR, GCR)
2. **Configure resource limits** based on actual usage
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure logging** (ELK stack, Fluentd)
5. **Set up backup** for persistent volumes
6. **Configure SSL/TLS** for ingress
7. **Use secrets** for sensitive data
8. **Set up network policies** for security
