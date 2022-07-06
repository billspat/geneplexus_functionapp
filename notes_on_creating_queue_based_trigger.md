## creating queue-based function triggers

Following this blog post: https://medium.com/swlh/how-to-use-azure-queue-triggered-functions-and-why-7f651c9d3f8c

### resource creation

Terraform creates and outputs resource group ( AZRG ), storage account (AZSA), 


### keys and secrets

*Getting the account key to get the storage account*



```
AZSA_queue="jobprocessing"
AZSA_container="jobs"
AZSA_table="jobstatus"
 
AZRG=$(terraform output -raw AZRG)
AZSA=$(terraform output -raw AZSA)
AZFN=$(terraform output -raw AZFN) 

TFDIR=../Terraform/  # or just "."
AZRG=$(terraform output -state $TFDIR/terraform.tfstate -raw AZRG)
AZSA=$(terraform output -state $TFDIR/terraform.tfstate -raw AZSA)
AZFN=$(terraform output  -state $TFDIR/terraform.tfstate -raw AZFN) 

AZSA_CONNSTR=$(az storage account show-connection-string --name $AZSA -g $AZRG --query 'connectionString')

SAKEY=$(az storage account keys list --resource-group $AZRG --account-name $AZSA --query '[1].value')

az functionapp config appsettings list  -n $AZFN -g $AZRG
az functionapp config appsettings set  -n $AZFN -g $AZRG --settings "QUEUECONNECTIONSTRING=$AZSA_CONNSTR"


```

host file on remote whic sets these settings?

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "{AzureWebJobsStorage}",
    "QueueConnectionString": $AZSA_CONNSTR,
    "STORAGE_CONTAINER_NAME": "jobs",
    "STORAGE_TABLE_NAME": "jobstatus"
  }
}

```

# 


## Publishing the code into the function app

func azure functionapp publish $AZFN

input to the queue processor is a list of items (document files in the blog post example, but that can be adapted to be jobs)



## testing with curl
curl command to test queue processing:

```sh

LOCALURL='http://localhost:7071/api/TriggerProcessing'
AZURL="https://$AZFN.azurewebsites.net/api/triggerprocessing"
curl --request POST --location $LOCALURL \
 --header 'Content-Type: application/json' \
 --data-raw '{"documentList": ["sample_file11.txt", "sample_file12.txt", "sample_file13.txt", "sample_file14.txt", "sample_file15.txt"]}'

curl -X POST $LOCALURL -H "Content-Type: application/json"    -d '{"documentList": ["sample_file1.txt", "sample_file2.txt", "sample_file3.txt", "sample_file4.txt", "sample_file5.txt"]}'


curl -X POST $AZURL -H "Content-Type: application/json"    -d '{"documentList": ["sample_file1.txt", "sample_file2.txt"]}'

'#, "sample_file3.txt", "sample_file4.txt", "sample_file5.txt"]}'


```

work plan

issue: skeleton app wasn't working due to config error,  get that working and tested

issue: function app is 3.9 which MS doesn't have by default so 

1) use custom docker container (don't want to do this)
2) set python to be 3.8  - where is this set?
3) use a different venv and somehow use that, need to figure out storage access

issue: call genepleusml instead of simple job thing

issue: how the app works is not well docmented 
    create new diagram of how things are set-up

current app does this: 

trigger : send 'docummentlis't of document file names  => send joblist of jobids (and in future an api key)
    future check that job id belongs to use with key
    future check that job has not been run yet

trigger 'triggerprocessing' has output of the queue , so automatically puts document file name  into queue
    https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-output?tabs=in-process%2Cextensionv5&pivots=programming-language-python

     => rename to 'jobtrigger' put job id into queue from joblist.  in addition to jobid, what else is needed? 
        parameters, could be read from the job info file.  
        
    future : mechanism to secure these jobids also, to prevent just putting jobid into the queue
    future 

processjob : input binding is queue, reads document filename, then reads the document and processes it
    https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-storage-queue-triggered-function

    

issue: post 