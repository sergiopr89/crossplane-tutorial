#!/bin/bash

helm repo add localstack-repo https://helm.localstack.cloud
helm repo update

helm upgrade --install localstack localstack-repo/localstack --namespace localstack --create-namespace
