terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.15.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }

  backend "azurerm" {
    resource_group_name  = "explore-azure-active-directory-b2c-project-gwc-rg"
    storage_account_name = "eaadb2cpprodsa"
    container_name       = "eaadb2c-terraform"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = "012e925b-f538-41ef-8d23-b0c85e7dbe7b"
}

provider "random" {}
