## geneplexus project: function app terraform main.tf
# this creates resources to run the PythonGeneplexus package as an azure function
# see the readme.md in the folder above for details


terraform {
  required_version = ">=1.1"

  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "~>3.7"
    }
  }

}

############
# providers
provider "azurerm" {
  features {}
}

# for random id used in tags
provider "random"{}

# for timestamp() function used in tags
provider "time"{} 

resource "random_string" "random_id" {
  length  = 6
  numeric  = false
  upper   = false
  special = false
}


############ variables
#####
# existing resources

variable "existing_storage_account_rg" {
  type = string

}

variable "existing_storage_account_name" {
  type = string

}

#####
# project level variables (used to name and tag things)

variable "project" {
  description = "Name of project, used in naming resources and tags"
  type = string
  default = "geneplexusml"
}

variable "env" {
  description = "working environment (dev, prod, test, training)"
  type = string
  default = "dev"
}

variable "location" {
  description = "Azure location name"
  type = string
  default = "Central US"
}

variable "userid" {
  description = "Id of user for use in tagging resources"
  type = string
  default = ""
}


############
# azure functions configuration options

variable "azure_functions_environment" {
  type = string
  description = "Development, Staging, or Production "
  default = "Development"

}

variable "python_enable_debug_logging" {
  type = number
  description = "1 to turn on debug, 0 off. set to 0 for production environments. default 1"
  default = 1

}

variable "function_app_sku_name" {
  type = string
  description = "Function SKU for Elastic or Consumption function app plans (Y1, EP1, EP2, and EP3)"
  default =  "Y1"
}           


########## 
#computed variables (locals)

locals {
  # Common tags to be assigned to all resources
  # id number can be used to select and delete resources
  common_tags = {
    created_by = var.userid
    project   = var.project
    environment = var.env
    created_on = timestamp()
    id = random_string.random_id.result
  }
}


############
# existing resources to tie in 

data "azurerm_storage_account" "geneplexus_storage" {
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/storage_account
  name                = var.existing_storage_account_name
  resource_group_name = var.existing_storage_account_rg
}

# azurerm_storage_account.geneplexus_storage.primary_access_key , primary_file_endpoint 

############
# resources

resource "azurerm_resource_group" "main" {
  name     = "${var.project}-${var.env}-rg"
  location = var.location

  tags = "${local.common_tags}"
}

output "AZRG" {
  value = azurerm_resource_group.main.name
  description = "resource group"
}


resource "azurerm_storage_account" "main" {
  name                     = "${var.project}${var.env}sa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags = "${local.common_tags}"
}



resource "azurerm_service_plan" "ml_runner" {
  name                = "${var.project}-${var.env}-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            =  var.function_app_sku_name

  tags = "${local.common_tags}"

}


resource "azurerm_linux_function_app" "ml_runner" {
  name                = "${var.project}-${var.env}-fn"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  storage_account_name = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key

  service_plan_id      = azurerm_service_plan.ml_runner.id

  # list of all app settings : https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings
  app_settings  = {
    FUNCTIONS_WORKER_RUNTIME = "python",
    AZURE_FUNCTIONS_ENVIRONMENT = var.azure_functions_environment,
    PYTHON_ENABLE_DEBUG_LOGGING = var.python_enable_debug_logging
  }

  site_config {
    application_stack {
      python_version = "3.9"
    }

  # mount a file share - can't find TF documentation on this
  provisioner "local-exec" {

command = <<-CMD
az webapp config storage-account add -g ${var.existing_storage_account_rg} \
-n ${var.existing_storage_account_name} \
--custom-id ${var.x} \
--storage-type AzureFiles \
--account-name ${azurerm_storage_account.geneplexus_storage.name} \
--share-name ${azurerm_storage_account.geneplexus_storage.primary_file_endpoint} \
--access-key ${azurerm_storage_account.geneplexus_storage.primary_access_key} \
--mount-path /data
CMD

}
  }

  tags = "${local.common_tags}"
}

######## 

output "function_app_id" {
  value = azurerm_linux_function_app.ml_runner.id
  description = "function app id"
}

output "AZFN" {
  value = azurerm_linux_function_app.ml_runner.name
  description = "function app name"
}

output "function_app_default_hostname" {
  value = azurerm_linux_function_app.ml_runner.default_hostname
  description = "function app hostname"
}
