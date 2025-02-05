locals {
  sa = {
    frontend = {
      replicas = [
        {
          name     = "${var.project_name}webapp${terraform.workspace}gwcsa"
          location = var.germanywestcentral_location
        }
      ]
    }
  }
}

resource "azurerm_storage_account" "documents" {
  name                            = "${var.project_name}documents${terraform.workspace}gwcsa"
  resource_group_name             = azurerm_resource_group.main.name
  location                        = var.germanywestcentral_location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false

  blob_properties {
    change_feed_enabled = true
    versioning_enabled  = true
  }

  tags = merge(var.default_tags, {
    "Environment" = terraform.workspace
  })
}

resource "azurerm_storage_account" "aihub" {
  name                            = "${var.project_name}aihub${terraform.workspace}eussa"
  resource_group_name             = azurerm_resource_group.main.name
  location                        = var.eastus_location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false

  tags = merge(var.default_tags, {
    "Environment" = terraform.workspace
  })
}

resource "azurerm_storage_account" "frontend_replicas" {
  count                    = length(local.sa.frontend.replicas)
  name                     = local.sa.frontend.replicas[count.index].name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = local.sa.frontend.replicas[count.index].location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  is_hns_enabled = false

  tags = merge(var.default_tags, {
    "Environment" = terraform.workspace
  })
}

resource "azurerm_storage_container" "devicetype_documents" {
  name                  = "devicetype-documents"
  storage_account_id    = azurerm_storage_account.documents.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "frontend_replicas" {
  count                 = length(local.sa.frontend.replicas)
  name                  = "$web"
  storage_account_id    = azurerm_storage_account.frontend_replicas[count.index].id
  container_access_type = "blob"
}

resource "azurerm_storage_account_static_website" "frontend_replicas" {
  count              = length(local.sa.frontend.replicas)
  storage_account_id = azurerm_storage_account.frontend_replicas[count.index].id
  error_404_document = "index.html"
  index_document     = "index.html"
}
