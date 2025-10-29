# Table of contents 📖
In this lab, we’ll cover the following Crossplane topics:
1. [Install and configure the AWS provider](../provider/)
1. [Create your first managed resource: an S3 bucket](../managed_resource/)
1. [Make your own composition with two EC2 instances](../composition/)
1. [Develop a custom function in Python](../function/)
1. [Generate resources with prompts using OpenAI](../IaP/)
---

# Providers
Providers are the same like terraform but into Crossplane.  
You might find some providers as a pack of all resources or like in case of AWS, a single provider for each module (S3, EC2,...) inside the `AWS family` provider.

## Install and configure
First, create a dummy secret, for AWS provider as we are working in `localstack`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-creds
  namespace: crossplane-system
type: Opaque
stringData:
  creds: |
    [default]
    aws_access_key_id = test
    aws_secret_access_key = test
```

Next install the S3 and EC2 `providers`:
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v0.40.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-ec2
spec:
  package: xpkg.upbound.io/upbound/provider-aws-ec2:v0.40.0
```

At last, create a `providerconfig` with the activated modules, `s3` and `ec2` in this lab:
```yaml
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      name: aws-creds
      namespace: crossplane-system
      key: creds
  endpoint:
    hostnameImmutable: true
    services: [s3, ec2]
    url:
      type: Static
      static: http://localstack.localstack.svc.cluster.local:4566
  skip_credentials_validation: true
  skip_metadata_api_check: true
  skip_requesting_account_id: true
  s3_use_path_style: true

```

## List current providers
Now you can see the installed providers with:
```bash
$ kubectl get provider
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
provider-aws-ec2              True        False     xpkg.upbound.io/upbound/provider-aws-ec2:v0.40.0     20s
provider-aws-elb              True        False     xpkg.upbound.io/upbound/provider-aws-elb:v0.40.0     20s
provider-aws-s3               True        False     xpkg.upbound.io/upbound/provider-aws-s3:v0.40.0      20s
upbound-provider-family-aws   True        False     xpkg.upbound.io/upbound/provider-family-aws:v2.1.1   15s
```

We can get some new CRDs with the following command, we'll dive into it soon:
```bash
$ kubectl get crd | awk '/aws.upbound.io/ {print $1}'
...
bucketpolicies.s3.aws.upbound.io
bucketpublicaccessblocks.s3.aws.upbound.io
bucketreplicationconfigurations.s3.aws.upbound.io
bucketrequestpaymentconfigurations.s3.aws.upbound.io
buckets.s3.aws.upbound.io
...
```
