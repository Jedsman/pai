# Helm Deployment Guide

## Quick Start

```bash
# Install with defaults
helm install ai-task-manager ./helm

# Install with custom values
helm install ai-task-manager ./helm -f values-production.yaml

# Upgrade
helm upgrade ai-task-manager ./helm --set image.tag=v2.0.0
```

## Key Configuration

### Basic Settings
- `replicaCount`: Number of app replicas (default: 2)
- `image.repository`: Container image location
- `image.tag`: Image version to deploy

### GPU Resources
```yaml
resources:
  requests:
    nvidia.com/gpu: 1
  limits:
    nvidia.com/gpu: 1

nodeSelector:
  accelerator: nvidia-tesla-l4
```

### GKE Inference Gateway
```yaml
inferenceGateway:
  enabled: true
  hostname: ai-task-manager.your-domain.com
  
inferencePool:
  enabled: true
  replicas: 2
  criticality: standard  # critical, standard, sheddable
```

### Auto-scaling
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## Environment-Specific Deployments

### Development
```bash
helm install dev ./helm \
  --set replicaCount=1 \
  --set resources.requests.nvidia.com/gpu=0 \
  --set postgresql.enabled=true
```

### Production
```bash
helm install prod ./helm \
  --set autoscaling.enabled=true \
  --set monitoring.enabled=true \
  --set inferenceGateway.tls.enabled=true \
  -f values-production.yaml
```

## Dependencies

### PostgreSQL (Optional)
```yaml
postgresql:
  enabled: true
  auth:
    database: taskmanager
```

### Secrets
```bash
kubectl create secret generic ai-secrets \
  --from-literal=google-api-key=your-key
```

## Monitoring

### Enable ServiceMonitor
```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

### Custom Metrics
```yaml
autoscaling:
  customMetrics:
    - type: External
      external:
        metric:
          name: inference_pool_average_kv_cache_utilization
        target:
          averageValue: "70"
```

## Security

### Pod Security
- Non-root user (1000)
- Read-only filesystem
- Dropped capabilities

### Network Policies
```yaml
# Applied automatically in restricted namespaces
podSecurityContext:
  fsGroup: 2000
  runAsUser: 1000
  runAsNonRoot: true
```

## Troubleshooting

```bash
# Check deployment status
helm status ai-task-manager

# View values
helm get values ai-task-manager

# Debug rendering
helm template ai-task-manager ./helm --debug

# Rollback
helm rollback ai-task-manager 1
```