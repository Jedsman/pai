resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  # Networking
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  # Enable required addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  # Enable Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Enable GPU sharing
  node_pool_defaults {
    node_config_defaults {
      gcfs_config {
        enabled = true
      }
    }
  }
}

resource "google_container_node_pool" "gpu_nodes" {
  name       = var.node_pool_name
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.min_node_count

  # Auto-scaling
  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  # Node configuration
  node_config {
    preemptible  = false
    machine_type = var.machine_type

    # GPU configuration
    guest_accelerator {
      type  = var.gpu_type
      count = var.gpu_count
      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }
    }

    # Service account
    service_account = google_service_account.gke_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Taints for GPU nodes
    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }

    labels = {
      accelerator = var.gpu_type
    }

    tags = ["gpu-node"]
  }

  # Update strategy
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}
