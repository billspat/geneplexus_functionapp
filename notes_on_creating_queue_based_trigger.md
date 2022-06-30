## creating queue-based function triggers

Following this blog post: https://medium.com/swlh/how-to-use-azure-queue-triggered-functions-and-why-7f651c9d3f8c

### resource creation

Terraform creates and outputs resource group ( AZRG ), storage account (AZSA), 


### keys and secrets

*Getting the account key to get the storage account*



```
AZSA_queue="jobprocessing"
AZSA_container=""
AZSA_table="jobstatus"
 

AZRG=$(terraform output -raw AZRG)
AZSA=$(terraform output -raw AZSA)

AZSA_CONNSTR=$(az storage account show-connection-string --name $AZSA -g $AZRG --query 'connectionString')

SAKEY=$(az storage account keys list --resource-group $AZRG --account-name $AZSA --query '[1].value')


```

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "{AzureWebJobsStorage}",
    "QueueConnectionString": $AZSA_CONNSTR,
    "STORAGE_CONTAINER_NAME": "testdocs",
    "STORAGE_TABLE_NAME": "status"
  }
}

```
