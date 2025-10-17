##############################################################################
# NYCU Course Platform - Terraform Infrastructure Configuration
# Provider: DigitalOcean / AWS / GCP (configurable)
##############################################################################

terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state management (recommended for production)
  backend "s3" {
    bucket = "nycu-platform-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Provider Configuration
provider "digitalocean" {
  token = var.do_token
}

provider "aws" {
  region = var.aws_region
}

##############################################################################
# VARIABLES
##############################################################################

variable "do_token" {
  description = "DigitalOcean API Token"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS Region"
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  default     = "nycu-course-platform"
}

variable "domain" {
  description = "Domain name"
  default     = "nymu.com.tw"
}

variable "server_size" {
  description = "Server size"
  default     = "s-4vcpu-8gb" # Suitable for 70K+ courses
}

##############################################################################
# DATA SOURCES
##############################################################################

data "digitalocean_ssh_key" "main" {
  name = "nycu-platform-key"
}

data "digitalocean_project" "main" {
  name = var.project_name
}

##############################################################################
# NETWORKING
##############################################################################

# VPC for isolation
resource "digitalocean_vpc" "main" {
  name     = "${var.project_name}-vpc"
  region   = "sgp1"
  ip_range = "10.0.0.0/16"
}

# Firewall rules
resource "digitalocean_firewall" "web" {
  name = "${var.project_name}-firewall"

  droplet_ids = [digitalocean_droplet.web.id]

  # Inbound rules
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"] # Restrict to specific IPs in production
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }

  # Monitoring ports (restrict to monitoring servers)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "9090" # Prometheus
    source_addresses = ["10.0.0.0/16"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "3000" # Grafana
    source_addresses = ["10.0.0.0/16"]
  }

  # Outbound rules
  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0"]
  }
}

##############################################################################
# COMPUTE INSTANCES
##############################################################################

# Main web server
resource "digitalocean_droplet" "web" {
  name     = "${var.project_name}-web-01"
  size     = var.server_size
  image    = "ubuntu-22-04-x64"
  region   = "sgp1"
  vpc_uuid = digitalocean_vpc.main.id

  ssh_keys = [data.digitalocean_ssh_key.main.id]

  monitoring         = true
  backups           = true
  ipv6              = true
  droplet_agent     = true

  user_data = templatefile("${path.module}/user-data.sh", {
    project_name = var.project_name
    domain       = var.domain
    environment  = var.environment
  })

  tags = [
    "web",
    "production",
    var.project_name
  ]
}

# Reserved IP for high availability
resource "digitalocean_floating_ip" "main" {
  droplet_id = digitalocean_droplet.web.id
  region     = digitalocean_droplet.web.region
}

# Database server (if needed for scaling)
resource "digitalocean_droplet" "database" {
  count    = var.environment == "production" ? 1 : 0

  name     = "${var.project_name}-db-01"
  size     = "s-2vcpu-4gb"
  image    = "ubuntu-22-04-x64"
  region   = "sgp1"
  vpc_uuid = digitalocean_vpc.main.id

  ssh_keys = [data.digitalocean_ssh_key.main.id]

  monitoring         = true
  backups           = true
  ipv6              = false
  droplet_agent     = true

  tags = [
    "database",
    "production",
    var.project_name
  ]
}

##############################################################################
# MANAGED DATABASE (Alternative to SQLite for scaling)
##############################################################################

resource "digitalocean_database_cluster" "postgres" {
  count = var.environment == "production" ? 0 : 0 # Set to 1 to enable

  name       = "${var.project_name}-db"
  engine     = "pg"
  version    = "15"
  size       = "db-s-2vcpu-4gb"
  region     = "sgp1"
  node_count = 2 # High availability

  maintenance_window {
    day  = "sunday"
    hour = "02:00:00"
  }

  tags = [var.project_name, "production"]
}

##############################################################################
# STORAGE
##############################################################################

# S3-compatible object storage for backups
resource "digitalocean_spaces_bucket" "backups" {
  name   = "${var.project_name}-backups"
  region = "sgp1"
  acl    = "private"

  lifecycle_rule {
    id      = "backup-retention"
    enabled = true

    expiration {
      days = 90 # Keep backups for 90 days
    }

    noncurrent_version_expiration {
      days = 30
    }
  }

  versioning {
    enabled = true
  }
}

# CDN for static assets
resource "digitalocean_cdn" "main" {
  origin         = digitalocean_spaces_bucket.backups.bucket_domain_name
  custom_domain  = "cdn.${var.domain}"

  ttl = 3600

  certificate_name = digitalocean_certificate.main.name
}

##############################################################################
# LOAD BALANCER
##############################################################################

resource "digitalocean_loadbalancer" "main" {
  name     = "${var.project_name}-lb"
  region   = "sgp1"
  vpc_uuid = digitalocean_vpc.main.id

  forwarding_rule {
    entry_protocol  = "https"
    entry_port      = 443
    target_protocol = "http"
    target_port     = 80

    certificate_name = digitalocean_certificate.main.name
  }

  forwarding_rule {
    entry_protocol  = "http"
    entry_port      = 80
    target_protocol = "http"
    target_port     = 80
  }

  healthcheck {
    protocol               = "http"
    port                   = 80
    path                   = "/api/health"
    check_interval_seconds = 10
    response_timeout_seconds = 5
    unhealthy_threshold    = 3
    healthy_threshold      = 2
  }

  sticky_sessions {
    type               = "cookies"
    cookie_name        = "lb"
    cookie_ttl_seconds = 300
  }

  droplet_ids = [digitalocean_droplet.web.id]

  redirect_http_to_https = true
  enable_proxy_protocol  = true
  enable_backend_keepalive = true

  size = "lb-small" # Can handle 10,000 concurrent connections
}

##############################################################################
# SSL/TLS CERTIFICATE
##############################################################################

resource "digitalocean_certificate" "main" {
  name    = "${var.project_name}-cert"
  type    = "lets_encrypt"
  domains = [var.domain, "www.${var.domain}"]

  lifecycle {
    create_before_destroy = true
  }
}

##############################################################################
# DNS RECORDS
##############################################################################

resource "digitalocean_domain" "main" {
  name = var.domain
}

resource "digitalocean_record" "a" {
  domain = digitalocean_domain.main.id
  type   = "A"
  name   = "@"
  value  = digitalocean_loadbalancer.main.ip
  ttl    = 300
}

resource "digitalocean_record" "www" {
  domain = digitalocean_domain.main.id
  type   = "CNAME"
  name   = "www"
  value  = "@"
  ttl    = 300
}

resource "digitalocean_record" "mx" {
  domain   = digitalocean_domain.main.id
  type     = "MX"
  name     = "@"
  priority = 10
  value    = "mail.${var.domain}."
  ttl      = 300
}

##############################################################################
# MONITORING & ALERTS
##############################################################################

resource "digitalocean_monitor_alert" "cpu" {
  alerts {
    email = ["admin@nymu.com.tw"]
    slack {
      channel = "alerts"
      url     = var.slack_webhook_url
    }
  }

  window      = "5m"
  type        = "v1/insights/droplet/cpu"
  compare     = "GreaterThan"
  value       = 80
  enabled     = true
  entities    = [digitalocean_droplet.web.id]
  description = "CPU usage is above 80%"
}

resource "digitalocean_monitor_alert" "memory" {
  alerts {
    email = ["admin@nymu.com.tw"]
  }

  window      = "5m"
  type        = "v1/insights/droplet/memory_utilization_percent"
  compare     = "GreaterThan"
  value       = 85
  enabled     = true
  entities    = [digitalocean_droplet.web.id]
  description = "Memory usage is above 85%"
}

##############################################################################
# AUTO-SCALING (Using DO App Platform for container-based deployment)
##############################################################################

resource "digitalocean_app" "main" {
  count = var.environment == "production" ? 0 : 0 # Set to 1 to enable

  spec {
    name   = var.project_name
    region = "ams"

    domain {
      name = var.domain
      type = "PRIMARY"
    }

    # Frontend service
    service {
      name               = "frontend"
      environment_slug   = "node-js"
      instance_count     = 2
      instance_size_slug = "professional-xs"

      git {
        repo_clone_url = "https://github.com/nycu/course-platform.git"
        branch         = "main"
      }

      build_command = "npm run build"
      run_command   = "npm start"

      http_port = 3000

      health_check {
        http_path            = "/api/health"
        initial_delay_seconds = 10
        period_seconds       = 10
        timeout_seconds      = 3
        success_threshold    = 1
        failure_threshold    = 3
      }

      env {
        key   = "NODE_ENV"
        value = "production"
      }
    }

    # Backend service
    service {
      name               = "backend"
      environment_slug   = "python"
      instance_count     = 3
      instance_size_slug = "professional-s"

      git {
        repo_clone_url = "https://github.com/nycu/course-platform.git"
        branch         = "main"
      }

      build_command = "pip install -r requirements.txt"
      run_command   = "uvicorn main:app --host 0.0.0.0 --port 8000"

      http_port = 8000

      health_check {
        http_path = "/health"
      }

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.postgres[0].uri
        type  = "SECRET"
      }
    }
  }
}

##############################################################################
# OUTPUTS
##############################################################################

output "web_server_ip" {
  value       = digitalocean_droplet.web.ipv4_address
  description = "The IPv4 address of the web server"
}

output "floating_ip" {
  value       = digitalocean_floating_ip.main.ip_address
  description = "The floating IP address"
}

output "load_balancer_ip" {
  value       = digitalocean_loadbalancer.main.ip
  description = "The load balancer IP address"
}

output "backup_bucket_endpoint" {
  value       = digitalocean_spaces_bucket.backups.bucket_domain_name
  description = "The S3-compatible backup bucket endpoint"
}

output "monthly_cost_estimate" {
  value = {
    droplet_web     = "$48/month (s-4vcpu-8gb)"
    droplet_db      = "$24/month (s-2vcpu-4gb) - optional"
    load_balancer   = "$12/month"
    backups         = "$0.50/month (automated)"
    spaces          = "$5/month (250GB)"
    bandwidth       = "$0.01/GB after 1TB"
    total_minimum   = "$65.50/month"
    total_with_db   = "$89.50/month"
  }
  description = "Estimated monthly costs"
}