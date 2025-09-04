output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.primary.name
}

output "cluster_location" {
  description = "GKE cluster location"
  value       = google_container_cluster.primary.location
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.gke_sa.email
}