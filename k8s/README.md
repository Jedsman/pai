# Kubernetes Manifests Guide

## Quick Deploy

```bash
# Install Inference Gateway CRDs
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api-inference-extension/releases/download/v0.3.0/manifests.yaml

# Deploy application
kubectl apply -f k8s/
```

## Core Components

### InferencePool
Manages AI model serving pods with GPU resources:
```yaml
# k8s/inference-pool.yml
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: vllm-server
        resources:
          requests:
            nvidia.com/gpu: 1
```

### InferenceModel
Defines model serving properties:
```yaml
spec:
  modelName: "ai-task-manager"
  poolRef:
    name: ai-task-manager-pool
  criticality: "standard"
  targetLatency: "2s"
```

### Gateway & HTTPRoute
Handles AI-aware load balancing:
```yaml
# Routes AI requests to InferencePool
# Routes regular requests to standard Service
```

## Required Secrets

```bash
# API keys
kubectl create secret generic api-secrets \
  --from-literal=google-api-key=your-key

# TLS certificate
kubectl create secret tls inference-tls-cert \
  --cert=tls.crt --key=tls.key
```

## Node Requirements

### GPU Nodes
- NVIDIA L4 GPUs
- Taint: `nvidia.com/gpu=present:NoSchedule`
- Label: `accelerator=nvidia-tesla-l4`

### Setup
```bash
# Enable GPU drivers
gcloud container node-pools create gpu-pool \
  --accelerator type=nvidia-tesla-l4,count=1 \
  --machine-type n1-standard-4 \
  --enable-autoscaling --min-nodes=1 --max-nodes=3
```

## Monitoring

### Health Checks
- Liveness: `/health` (60s delay)
- Readiness: `/health` (30s delay)

### Metrics
- Prometheus scraping on `:8000/metrics`
- Custom AI metrics for HPA scaling

## Troubleshooting

```bash
# Check InferencePool status
kubectl get inferencepool
kubectl describe inferencepool ai-task-manager-pool

# Check Gateway
kubectl get gateway
kubectl get httproute

# GPU allocation
kubectl describe nodes | grep nvidia.com/gpu

# Logs
kubectl logs -l app=ai-task-manager
```

**Taints & Tolerations** ensure GPU nodes only run GPU workloads:

**How it works:**
1. **Taint on GPU nodes**: `nvidia.com/gpu=present:NoSchedule` 
2. **Effect**: Regular pods can't schedule on these expensive nodes
3. **Toleration on GPU pods**: Allows them to "tolerate" the taint and schedule

**Example:**
```yaml
# Node gets tainted (automatically by GKE)
taint:
  key: nvidia.com/gpu
  value: present
  effect: NoSchedule

# Pod needs matching toleration
tolerations:
- key: "nvidia.com/gpu"
  operator: "Equal" 
  value: "present"
  effect: "NoSchedule"
```

**Benefits:**
- Prevents CPU-only workloads from wasting GPU nodes
- Ensures GPU availability for AI workloads
- Cost optimization by proper resource allocation

**Taint Effects:**
- `NoSchedule`: Don't schedule new pods
- `PreferNoSchedule`: Avoid if possible
- `NoExecute`: Evict existing pods

**NoSchedule vs other effects:**

- NoSchedule: New pods can't schedule, but existing pods stay
- NoExecute: Evicts all existing pods immediately
- PreferNoSchedule: Soft constraint, may still schedule if needed