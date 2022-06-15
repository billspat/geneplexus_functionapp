## Azure Function for running Geneplexus ML jobs

### Project Structure

Two main folders: 
 - "function_app"  :  main project folder (<project_root>), python code for  Azure function itself.  
                    Zip this one for zip deployment
 -  Terraform       : code to create the resources in azure to deploy


The main project folder (<project_root>) can contain the following files:

* **local.settings.json** - Used to store app settings and connection strings when running locally. This file doesn't get published to Azure. To learn more, see [local.settings.file](https://aka.ms/azure-functions/python/local-settings).
* **requirements.txt** - Contains the list of Python packages the system installs when publishing to Azure.
* **host.json** - Contains global configuration options that affect all functions in a function app. This file does get published to Azure. Not all options are supported when running locally. To learn more, see [host.json](https://aka.ms/azure-functions/python/host.json).
* **Dockerfile** - (Optional) Used when publishing your project in a [custom container](https://aka.ms/azure-functions/python/custom-container).
* **tests/** - (Optional) Contains the test cases of your function app. For more information, see [Unit Testing](https://aka.ms/azure-functions/python/unit-testing).
* **.funcignore** -  Declares files that shouldn't get published to Azure. Terraform/ and .vscode/ to ignore your editor setting, .venv/ to ignore local Python virtual environment if you are using virtual env, tests/ to ignore test cases, and local.settings.json to prevent local app settings being published.

Each function has its own code file and binding configuration file ([**function.json**](https://aka.ms/azure-functions/python/function.json)).
 


### running locally
1. create a virtual environment.   Anaconda may also work, but for M1 mac using virtualenv works. 
    1. note you can install this venv any where, but many examples install in the project folder.  This is just an example... in this root folder of this project
    1. virtualenv -p python3 .venv
    1. source .venv/bin/activate
    1. pip install -r geneplexus_job/requirements.txt

1. install azure function core tools. 
    1.  https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=v4%2Cmacos%2Ccsharp%2Cportal%2Cbash
    1. note the 'func' utility does not work on new Mac with M1 chip, so in teh terminal start rosetta with `arch i386` then install homebrew and use homebrew in the i386 terminal 
    
1. download GP data: 
    The function app expects two folders to be present : DATA_PATH where the backend data is stored and JOBS_PATH where job folders can be found.  They do not have to be in the same tree (on Azure it's just more convenient that they share a parent folder).
    The data is ~30gb 
    1. create a path on your computer that can hold 30gb of back end data
    1. install the PyGenePlexus package in your Python3 environment
    1. install python_dotenv
    1. set the variable DATA_PATH in your shell to the full path from step 1. 
    1. `python3 download_data_for_geneplexus.py` 

1. create folder to hold jobs.   Each job has a subfolder inside that.   There 
1. create local settings file
    1. copy `example-local.settings.json` to `local.settings.json`
    1. edit `local.settings.json` per instructions in that file, using the datapath 
       you created above
1. create a job folder
    1. you need a job folder to read in genes file and save outputs, like the web app uses
       there is an examle job folder in this project    
    2. look up what's in your local_settings.json file from above, and run the following from the shell 
    ```
JOBS_PATH=/path/from/localsettings/to/jobs
mkdir -p $JOBS_PATH
cp -r example_job_folder $JOBS_PATH/example_job
    ```


1. run function from the command line.  note Azure tutorials and examples say to use VS code but you can run from command line too. 

    1. cd to `function_app` folder
    1. `func start`
    1. note the port that it starts on, usually 7071.  
    1. go to http://localhost:7071/api/geneplexus_job?jobid=example_job

   
## Build Process Using the CLI to create this function app

1. log-in to azure with `az login`
1. check your subscription with `az account show`  to ensure it's the subscription you intend

#### Creating resources with Terraform

1. cd to the terraform folder
1. in the Terraform folder, create a tfvars file for your specific settings, e.g. `dev.tfvars`
2. create a plan with `terraform plan -var-file=dev.tfvars -out=dev.plan`
3. apply the plan with `terraform apply "dev.plan" ` 
4. capture the output of the resource group and fucntion app name
5. see the script `Terraform/file_share.sh` to mount a file share to the function app and available at the mountpoint in that script
    (this should be incorporated into main.tf as a localexec provisioner)
    this requires access to the `azuredeploy.sh` script from the geneplexus app folder, and the data present in the share file to work

#### Publishing your function app to Azure 

Use [zip deployment](https://docs.microsoft.com/en-us/azure/azure-functions/deployment-zip-push) with the cli

1. zip the main folder  `cd function_app; rm ../function_app.zip ; zip -r -D ../function_app.zip *`
1. `az functionapp deployment source config-zip -g <resource_group> -n <app_name> --src <zip_file_path>`

For more information on all deployment options for Azure Functions, please visit this [guide](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python#publish-the-project-to-azure).

#### Next Steps

* To learn more specific guidance on developing Azure Functions with Python, please visit [Azure Functions Developer Python Guide](https://aka.ms/azure-functions/python/python-developer-guide).