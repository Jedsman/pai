terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "your-terraform-state-bucket"
    prefix = "ai-task-manager/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}