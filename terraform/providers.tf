terraform {
  required_version = ">=0.12"

  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = "~>1.5"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}

provider "azapi" {
}

provider "azurerm" {
  features {}

  // add after az login 
  # tenant_id       = "000000000000000000000000"
  # subscription_id = "000000000000000000000000"
}