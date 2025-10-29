# Table of contents 📖
In this lab, we’ll cover the following Crossplane topics:
1. [Install and configure the AWS provider](../provider/)
1. [Create your first managed resource: an S3 bucket](../managed_resource/)
1. [Make your own composition with two EC2 instances](../composition/)
1. [Develop a custom function in Python](../function/)
1. [Generate resources with prompts using OpenAI](../IaP/)
---

# Managed resources
Managed resources are objects in kubernetes that represents a living infrastructure component, like an AWS S3 `Bucket` or EC2 `Instance`.

## Create and list a S3 bucket
First, apply the following manifest:
```yaml
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: test-bucket
spec:
  forProvider:
    region: us-east-1
```

After few seconds, you will be able to see the resource *READY* and *SYNCED*:
```bash
$ kubectl get buckets
NAME          READY   SYNCED   EXTERNAL-NAME   AGE
test-bucket   True    True     test-bucket     85s
```

List the resource in the CLI:
```bash
$ awslocal s3 ls
2025-10-21 15:56:50 test-bucket
```

Now delete it:
```bash
$ kubectl delete bucket test-bucket
bucket.s3.aws.upbound.io "test-bucket" deleted
$ awslocal s3 ls
```

That’s it! You’re now ready to create and delete basic infrastructure as code with Crossplane, and take advantage of Kubernetes’ reconciliation loop to keep your infrastructure status up to date.  
In the next topic, we’ll cover compositions—a way to define an abstract set of infrastructure components that anyone can create by simply filling in the input variables of a contract.
