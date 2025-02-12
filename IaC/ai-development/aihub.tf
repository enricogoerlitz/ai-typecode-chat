# resource "random_string" "ai_project" {
#   length  = 6
#   lower   = true
#   upper   = false
#   special = false
#   numeric = false
# }

# resource "azapi_resource" "hub" {
#   type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
#   name      = "${var.project_name}-${terraform.workspace}-eus-aih"
#   location  = var.eastus_location
#   parent_id = azurerm_resource_group.main.id

#   identity {
#     type = "SystemAssigned"
#   }

#   body = {
#     properties = {
#       description    = "This is my Azure AI hub"
#       friendlyName   = "My AI Hub (dta)"
#       storageAccount = azurerm_storage_account.aihub.id
#       keyVault       = azurerm_key_vault.aihub.id

#       /* Optional: To enable these field, the corresponding dependent resources need to be uncommented.
#       applicationInsight = azurerm_application_insights.default.id
#       containerRegistry = azurerm_container_registry.default.id
#       */

#       /*Optional: To enable Customer Managed Keys, the corresponding 
#       encryption = {
#         status = var.encryption_status
#         keyVaultProperties = {
#             keyVaultArmId = azurerm_key_vault.default.id
#             keyIdentifier = var.cmk_keyvault_key_uri
#         }
#       }
#       */

#     }
#     kind = "hub"
#   }
# }

# // Azure AI Project
# resource "azapi_resource" "project" {
#   type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
#   name      = "device-type-agent-${random_string.ai_project.id}"
#   location  = var.eastus_location
#   parent_id = azurerm_resource_group.main.id

#   identity {
#     type = "SystemAssigned"
#   }

#   body = {
#     properties = {
#       description   = "This is my Azure AI PROJECT"
#       friendlyName  = "My Project (dta)"
#       hubResourceId = azapi_resource.hub.id
#     }
#     kind = "project"
#   }
# }