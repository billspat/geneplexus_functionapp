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


input to the queue processor is a list of items (document files in the blog post example, but that can be adapted to be jobs)

curl command to test queue processing:

```sh

LOCALURL='http://localhost:7071/api/TriggerProcessing'
AZURL="https://geneplexusml-dev-fn.azurewebsites.net/api/triggerprocessing"
curl --request POST --location $LOCALURL \
 --header 'Content-Type: application/json' \
 --data-raw '{"documentList": ["sample_file11.txt", "sample_file12.txt", "sample_file13.txt", "sample_file14.txt", "sample_file15.txt"]}'

curl -X POST $LOCALURL -H "Content-Type: application/json"    -d '{"documentList": ["sample_file1.txt", "sample_file2.txt", "sample_file3.txt", "sample_file4.txt", "sample_file5.txt"]}'


curl -X POST $AZURL -H "Content-Type: application/json"    -d '{"documentList": ["sample_file1.txt", "sample_file2.txt", "sample_file3.txt", "sample_file4.txt", "sample_file5.txt"]}'


```