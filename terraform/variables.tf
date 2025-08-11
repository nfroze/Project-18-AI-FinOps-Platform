variable "region" {
  description = "AWS region"
  default     = "eu-west-2"
}

variable "grafana_admin_password" {
  description = "Admin password for Grafana"
  type        = string
  sensitive   = true
  # No default - Terraform will prompt for password
}