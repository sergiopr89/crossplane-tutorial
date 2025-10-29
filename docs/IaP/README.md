# Table of contents 📖
In this lab, we’ll cover the following Crossplane topics:
1. [Install and configure the AWS provider](../provider/)
1. [Create your first managed resource: an S3 bucket](../managed_resource/)
1. [Make your own composition with two EC2 instances](../composition/)
1. [Develop a custom function in Python](../function/)
1. [Generate resources with prompts using OpenAI](../IaP/)
---

# Infrastructure as Prompt
## ABout
The idea is to replace large logic and definitions by natual language and let the AI generate all the specific code.  

## Setup
### Install the function
Like we already done with the patch function, we will use an OpenAI integration function. Install it with:
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: upbound-function-openai
spec:
  package: xpkg.upbound.io/upbound/function-openai:v0.3.0
```

### Create a secret
Generate an API Key in OpenAI and save it, then create the following secret:
```yaml
apiVersion: v1
kind: Secret
metadata:
    name: gpt
    namespace: crossplane-system
data:
    OPENAI_API_KEY: <your api key in base64 here>
    # OPENAI_BASE_URL: 
    # Optional: Use custom OpenAI-compatible endpoint
    # Example: http://localhost:11434/v1
    # OPENAI_MODEL: 
    # Optional: Use custom model (defaults to gpt-4)
    # Example: gpt-oss:20b
```

## Create the XRD
Like berfore, we need a `CustomResourceDefinition`, we are going to use the same:
```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xbasicapps.example.com
spec:
  scope: Cluster
  group: example.com
  names:
    kind: XBasicApp
    plural: xbasicapps
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              instanceType:
                type: string
                default: t3.micro
              region:
                type: string
                default: us-east-1
              ami:
                type: string
                default: ami-dummy
            required: []
```

## Create the Composition
Now here it's where the game begins. We are going to include the OpenAI function and put a prompt that references the Managed Resources (Instances from AWS) and dinamically will send the XR data to the composition prompt to let the LLM generate the final resources. So, create the `composition` with:
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: compose-an-app-with-gpt
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: XBasicApp
  mode: Pipeline
  pipeline:
  - step: make-gpt-do-it
    functionRef:
      name: upbound-function-openai
    input:
      apiVersion: openai.fn.upbound.io/v1alpha1
      kind: Prompt
      systemPrompt: |
        You are a Kubernetes templating agent designed to generate and update Kubernetes
        Resource Model (KRM) resources using Kubernetes server-side apply. Your task is
        to create, update, or delete YAML manifests based on the provided composite
        resource and any existing composed resources.

        Respond with only valid YAML manifests.
      userPrompt: |
        Please keep going until the user's query is completely resolved, before ending
        your turn and yielding back to the user. Only terminate your turn when you are
        sure that the problem is solved.
        Please follow these instructions carefully:
        1. Analyze the provided composite resource and any existing composed resources.
        2. Analyze the input to understand what composed resources you should create,
           update, or delete. You may be asked to derive composed resources from the
           composite resource, or from other composed resources.
        3. Generate a stream of YAML manifests based on your analysis in steps 1 and 2.
           Each manifest must:
           a. Be valid for Kubernetes server-side apply (fully specified intent).
           b. Omit names and namespaces.
           c. Include an annotation with the key "upbound.io/name". This annotation
              must uniquely identify the manifest within the YAML stream. It must be
              lowercase, hyphen separated, and less than 30 characters long. Prefer
              to use the manifest's kind. If two or more manifests have the same
              kind, look for something unique about the manifest and append that to
              the kind. This annotation is used to match the manifests you return to
              any manifests that were passed you inside the <composed> tag, so if
              your intent is to update a manifest never change its "upbound.io/name"
              annotation. This is critically important.
           d. If it's necessary to use labels to create relationships between
              resources, use the name of the composite resource as the label value.
        4. If there are existing composed resources:
            a. You can update an existing composed resource by including it in your
               output with any changes you deem necessary based on the input. Try to
               reuse existing composed resource values as much as possible. Only
               change values when you're sure it's necessary.
            b. If the input indicates that a resource is no longer required, you can
               delete it by omitting it from your output.
        5. Your output must only be a stream of YAML manifests, each separated by
           "---".

        ---
        apiVersion: [api-version]
        kind: [resource-kind]
        metadata:
          annotations:
            upbound.io/name: [resource-kind]
          labels:
            [relationship-labels-if-needed]
        spec:
          [resource-specific-fields]
        ---
        [Additional resources as needed]

        Here is the composite resource you'll be working with:
        <composite>
        {{ .Composite }}
        </composite>
        If there are any existing composed resources, they will be provided here:
        <composed>
        {{ .Composed }}
        </composed>
        Additional input is provided here:

        Use the resource in the <composite> tag to template an EC2 instance: https://marketplace.upbound.io/providers/upbound/provider-aws-ec2/v2.1.1 
        with the apiGroup ec2.aws.upbound.io/v1beta1.
        Use the value at JSON path .spec.instanceType to set the Instance
        type. Use the value at JSON path .spec.region to set its
        region. Use the value at JSON path .spec.ami to set its
        ami. Hardcode the value "default" for spec.providerConfigRef.name
        in the composition.

        You have to create a pair of them with names: instance1 and instance2.
    credentials:
    - name: gpt
      source: Secret
      secretRef:
        namespace: crossplane-system
        name: gpt
```

## Create the XR with the instances specs
Now, like before, we will create the `CompositeResource` with the few vars that will tell the LLM which AMI, region and instance type to use:
```yaml
apiVersion: example.com/v1alpha1
kind: XBasicApp
metadata:
  name: webapp-example1
spec:
  instanceType: t3.nano
  region: us-east-1
  ami: ami-dummy
```

## Notes
At this point it will generate by you the pair of instances (instance1 and instance2) we defined in the prompt.  
If there is any error related with the function execution, you should be able to see any events on the `CustomResource` with:
```bash
$ kubectl describe xbasicapp webapp-example1
```
Some errors might include API errors like insufficient quota, auth errors or YAML parsing errors.  
If you want to see what is sent to the API but you don't have any observability tool in the middle, a quick workarround is to set in the secret the `OPENAI_BASE_URL` with `http://<HOST_IP>:8080/v1` in base64, start a socket in the host like `nc -lk 0.0.0.0 8080`.
