variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "your-gcp-project-id"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
  default     = "ai-task-manager-cluster"
}

variable "node_pool_name" {
  description = "Node Pool Name"
  type        = string
  default     = "gpu-pool"
}

variable "machine_type" {
  description = "Machine type for nodes"
  type        = string
  default     = "n1-standard-4"
}

variable "gpu_type" {
  description = "GPU type"
  type        = string
  default     = "nvidia-tesla-l4"
}

variable "gpu_count" {
  description = "Number of GPUs per node"
  type        = number
  default     = 1
}

variable "min_node_count" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum number of nodes"
  type        = number
  default     = 3
}