terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "studymate" {
  name         = "amircw/studymate-api:latest"
  keep_locally = false
}

resource "docker_container" "studymate" {
  name  = "studymate-terraform"
  image = docker_image.studymate.image_id

  ports {
    internal = 8000
    external = 8080
  }

  env = [
    "GROQ_API_KEY=${var.groq_api_key}"
  ]
}

variable "groq_api_key" {
  description = "Groq API key"
  type        = string
  sensitive   = true
}