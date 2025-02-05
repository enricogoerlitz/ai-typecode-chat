variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "dta"
}

variable "project_resourcegroup_name" {
  description = "The name of the resource group for the project"
  type        = string
  default     = "dta-project-gwc-rg"

}

variable "default_tags" {
  description = "The default tags for all resources"
  type        = map(string)
  default = {
    "Project" = "emtec-ai-device-type-agent"
  }
}

variable "westeurope_location" {
  description = "The location for the resources"
  type        = string
  default     = "westeurope"
}

variable "germanywestcentral_location" {
  description = "The location for the resources"
  type        = string
  default     = "germanywestcentral"
}

variable "northeurope_location" {
  description = "The location for the resources"
  type        = string
  default     = "northeurope"
}

variable "eastus_location" {
  description = "The location for the resources"
  type        = string
  default     = "eastus"
}

variable "eastus2_location" {
  description = "The location for the resources"
  type        = string
  default     = "eastus2"
}
