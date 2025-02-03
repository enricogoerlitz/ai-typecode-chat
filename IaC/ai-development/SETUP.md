# SETUP Datahub Infrastructure

## Prerequisites

1. Azure Subscription
2. Resource Group: `<YOUR_RESOURCE_GROUP>`
3. Storage Account: `<YOUR_BACKEND_STORAGE_ACCOUNT>`
4. Container: `<YOUR_BACKEND_STORAGE_ACCOUNT_CONTAINER>`
5. Terraform installed locally ("4.15.0")
6. Visual Studio Code

## Build Infrastructure

### Run Terraform Commands

```sh
# Setup terraform
$ terraform init
$ terraform workspace new dev
$ terraform workspace new qa
$ terraform workspace new prod
$ terraform workspace select dev

# Generate an session alias for easy terraform cmd management
$ alias tfplan='terraform plan -var-file=$(terraform workspace show).tfvars'
$ alias tfapply='terraform apply -var-file=$(terraform workspace show).tfvars -auto-approve'

# Execute cmd
$ tfplan
$ tfapply
```

## Manual Tasks
