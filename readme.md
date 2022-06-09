## Azure Function for running Geneplexus ML jobs

#### Project Structure

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
 

#### Using the CLI to create this function app

1. log-in to azure with `az login`
1. check your subscription with `az account show`  to ensure it's the subscription you intend

#### Creating resources with Terraform

1. cd to the terraform folder
1. in the Terraform folder, create a tfvars file for your specific settings, e.g. `dev.tfvars`
2. create a plan with `terraform plan -var-file=dev.tfvars -out=dev.plan`
3. apply the plan with `terraform apply "dev.plan" ` 
4. capture the output of the resource group and fucntion app name

#### Publishing your function app to Azure 

Use [zip deployment](https://docs.microsoft.com/en-us/azure/azure-functions/deployment-zip-push) with the cli

1. zip the main folder  cd function_app,  `zip * function_app.zip`
1. `az functionapp deployment source config-zip -g <resource_group> -n <app_name> --src <zip_file_path>`

For more information on all deployment options for Azure Functions, please visit this [guide](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python#publish-the-project-to-azure).

#### Next Steps

* To learn more specific guidance on developing Azure Functions with Python, please visit [Azure Functions Developer Python Guide](https://aka.ms/azure-functions/python/python-developer-guide).