# AI Task Manager - GCP Deployment Guide

## Prerequisites

```bash
# Install required tools
gcloud auth login
kubectl config current-context
helm version
terraform --version
```

## Quick Start

```bash
# 1. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 2. Deploy application
cd ../
helm install ai-task-manager ./helm --set image.tag=latest
```

## GCP-Native Integration

### Cloud Storage for Model Weights
```yaml
# values-production.yaml
storage:
  enabled: true
  bucket: "gs://your-model-weights-bucket"
  mountPath: "/app/models"
  
volumes:
  - name: gcs-fuse
    csi:
      driver: gcsfuse.csi.storage.gke.io
      volumeAttributes:
        bucketName: your-model-weights-bucket
```

### Cloud SQL Integration
```yaml
postgresql:
  enabled: false
  
cloudSQL:
  enabled: true
  instance: "project:region:instance-name"
  database: "taskmanager"
  
env:
  DATABASE_URL:
    valueFrom:
      secretKeyRef:
        name: cloudsql-secret
        key: database-url
```

### Workload Identity Setup
```bash
# Create Kubernetes Service Account
kubectl create serviceaccount ai-task-manager-ksa

# Create Google Service Account  
gcloud iam service-accounts create ai-task-manager-gsa

# Bind accounts
gcloud iam service-accounts add-iam-policy-binding \
  ai-task-manager-gsa@PROJECT.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT.svc.id.goog[default/ai-task-manager-ksa]"

# Annotate KSA
kubectl annotate serviceaccount ai-task-manager-ksa \
  iam.gke.io/gcp-service-account=ai-task-manager-gsa@PROJECT.iam.gserviceaccount.com
```

### Cloud Monitoring Integration
```yaml
# Custom metrics for AI workloads
monitoring:
  customMetrics:
    - inference_requests_total
    - inference_latency_seconds
    - kv_cache_utilization_percent
    - gpu_memory_usage_bytes
```

## Environment-Specific Deployments

### Development
```bash
helm install ai-task-manager ./helm \
  --set replicaCount=1 \
  --set resources.requests.nvidia.com/gpu=0 \
  --set postgresql.enabled=true
```

### Staging  
```bash
helm install ai-task-manager ./helm \
  --set inferenceGateway.hostname=staging.your-domain.com \
  --set cloudSQL.enabled=true \
  -f values-staging.yaml
```

### Production
```bash
helm install ai-task-manager ./helm \
  --set replicaCount=3 \
  --set autoscaling.enabled=true \
  --set monitoring.enabled=true \
  --set inferenceGateway.tls.enabled=true \
  -f values-production.yaml
```

## CI/CD with Cloud Build

### Build Configuration
```yaml
# cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-f', 'Dockerfile.gpu', '-t', 'gcr.io/$PROJECT_ID/ai-task-manager:$COMMIT_SHA', '.']
  
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/ai-task-manager:$COMMIT_SHA']
  
- name: 'gcr.io/cloud-builders/gke-deploy'
  args:
  - run
  - --filename=helm/
  - --image=gcr.io/$PROJECT_ID/ai-task-manager:$COMMIT_SHA
  - --cluster=$_CLUSTER_NAME
  - --location=$_CLUSTER_LOCATION
```

## Security Best Practices

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-task-manager-netpol
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: ai-task-manager
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: inference-gateway
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
```

### Pod Security Standards
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-workloads
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Scaling Strategies

### Vertical Pod Autoscaling
```bash
kubectl apply -f - <<EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ai-task-manager-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-task-manager
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: ai-task-manager
      maxAllowed:
        nvidia.com/gpu: 2
        memory: 8Gi
EOF
```

### Cluster Autoscaling
```bash
# Enable cluster autoscaler
gcloud container clusters update CLUSTER_NAME \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --zone=ZONE
```

## Monitoring & Observability

### Cloud Logging
```yaml
env:
  GOOGLE_CLOUD_PROJECT: "your-project-id"
  LOG_LEVEL: "INFO"
  STRUCTURED_LOGGING: "true"
```

### Custom Dashboards
```bash
# Import pre-built dashboard
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json
```

## Disaster Recovery

### Backup Strategy
```bash
# Backup persistent data
gcloud sql backups create --instance=INSTANCE_NAME

# Backup configurations
kubectl get all -o yaml > backup-$(date +%Y%m%d).yaml
```

### Multi-Region Setup
```bash
# Deploy to multiple regions
helm install ai-task-manager-us ./helm \
  --set nodeSelector.topology.kubernetes.io/zone=us-central1-a

helm install ai-task-manager-eu ./helm \
  --set nodeSelector.topology.kubernetes.io/zone=europe-west1-a
```

## Troubleshooting

### Common Issues
```bash
# Check GPU allocation
kubectl describe nodes | grep nvidia.com/gpu

# Debug inference gateway
kubectl logs -l app=inference-gateway -n gke-system

# Monitor resource usage
kubectl top pods --containers
```

### Performance Tuning
```yaml
resources:
  requests:
    nvidia.com/gpu: 1
    memory: "4Gi"
    ephemeral-storage: "10Gi"
  limits:
    nvidia.com/gpu: 1
    memory: "8Gi"
    ephemeral-storage: "20Gi"
```