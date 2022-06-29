# add_file_share.sh  
# this is a temporary script to learn how the CLI can be used to add file share
# to a function app.  This is necessary to connect the geneplexus data and job files
# so the function app can read/write them.   The goal is to move this into the terraform 
# provisioning script 

# edit this for your own computer - where is this folder?
gp_folder=$HOME/Code/krishnan_lab/geneplexus_app
# edit this to match current dev resource group
envsuffix=dev202205
source $gp_folder/azure/azuredeploy.sh
az_check_account 
az_set_vars $envsuffix

# names are from the output of terraform
# the resource group and name of your function. 
export AZFNRG=
export AZFN=

# existing storage
export AZSTORAGE_KEY=$(az storage account keys list --resource-group $AZRG --account-name $AZSTORAGENAME --query "[0].value" --output tsv)
export AZSTORAGE_CUSTOM_ID=$(az_get_app_identity)  # this function is defined in azuredeploy.sh

az webapp config storage-account add -g $AZFNRG -n $AZFN \
--custom-id $AZSTORAGE_CUSTOM_ID \
--storage-type AzureFiles \
--account-name $AZSTORAGENAME \
--share-name $AZSHARENAME \
--access-key $AZSTORAGE_KEY \
--mount-path /geneplexus_files

# permissions? 

# check it
az webapp config storage-account list --resource-group $AZFNRG --name $AZFN