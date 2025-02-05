resource "random_string" "aisearch" {
  length  = 6
  lower   = true
  upper   = false
  special = false
  numeric = false
}

resource "azurerm_search_service" "main" {
  name                = "${var.project_name}-${random_string.aisearch.id}-${terraform.workspace}-eus-as"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.eastus_location
  sku                 = "free"
}
