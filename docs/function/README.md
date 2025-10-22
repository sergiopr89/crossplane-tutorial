# Table of contents 📖
In this lab, we’ll cover the following Crossplane topics:
1. [Install and configure the AWS provider](../provider/)
1. [Create your first managed resource: an S3 bucket](../managed_resource/)
1. [Make your own composition with two EC2 instances](../composition/)
1. [Develop a custom function in Python](../function/)
---

# Functions
## About
Functions are a way to inject logic in the Composition execution. Like mutating a field from the **XR** to the **Composition** or checking an external feature flag API and make the **Composition** act dinamically, etc.

## Functions marketplace
You can look for a function at the [upbound marketplace](https://marketplace.upbound.io/functions) or develop and publish your own.

## Bootstrap the new function
Create a new function `function-replace-field` with the command:
```bash
crossplane xpkg init function-replace-field https://github.com/crossplane/function-template-python -d function-replace-field
```
In the current versions is just a repository template so we need to manually edit the `package/crossplane.yaml` and edit the `metadata.name` field with our function name.

## Edit the function logic
Replace the function logic in `function/fn.py` with:
```python
        rsp = response.to(req)

        # get all the replaces in there
        replaces = req.input["replaces"]

        for replace in replaces:
            # For each replace, obtain the required inputs
            field_path = replace["fromPath"]
            pattern = replace["pattern"]
            value = replace["value"]

            # Locate the container in desired XR
            container = rsp.desired.composite.resource
            keys = field_path.split(".")
            for key in keys[:-1]:
                if key not in container:
                    container[key] = {}
                container = container[key]
            last_key = keys[-1]

            # Apply regex on the observed XR value and store in desired XR
            observed_value = req.observed.composite.resource
            for key in keys:
                observed_value = observed_value[key]
            # Apply value update
            container[last_key] = re.sub(pattern, value, str(observed_value))

        return rsp
```
### Input, observed, desired
* `Input` is the **input** the field in the `Composition` object with the current value.  
* `Observed` is the actual value in the **XR** object.  
* `Desired` is the future value you want in the `Composition`

## Render to preview and try it
Create the following files:
```yaml
# XRD file
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: myxrd.example.crossplane.io
spec:
  group: example.crossplane.io
  names:
    kind: MyXRD
    plural: myxrds
  scope: Cluster
  versions:
    - name: v1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                region:
                  type: string
                name:
                  type: string
```
```yaml
# Composition file
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: create-infra
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: myXRD
  mode: Pipeline
  pipeline:
  - step: create-infra
    functionRef:
      name: function-replace-field
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
        - name: instance1
          base:
            apiVersion: ec2.aws.upbound.io/v1beta1
            kind: Instance
            spec:
              forProvider:
                ami: ami-dummy
                instanceType: t3.micro
                region: us-east-1
              providerConfigRef:
                name: default
      replaces:
        - fromPath: spec.name
          pattern: "-deploy.*"
          value: "-blue-deployment"
```
```yaml
# Function file
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-replace-field
  annotations:
    render.crossplane.io/runtime: Development
```
```yaml
# XR file
apiVersion: example.crossplane.io/v1
kind: myXRD
metadata:
  name: example-infra
spec:
  region: us-east-2
  name: some-deployment
```
Run the function in another terminal with:
```bash
$ python3 function/main.py --insecure

{"tag": "", "level": "info", "lineno": 22, "filename": "fn.py", "ts": 1761125591.9421225, "msg": "Running function"}
```
Run the follwing command to render it, note positional arguments are important:
```bash
crossplane render xr.yaml composition.yaml funtions.yaml --xrd=xrd.yaml --timeout=5s

---
apiVersion: example.crossplane.io/v1
kind: myXRD
metadata:
  name: example-infra
spec:
  name: some-blue-deployment
status:
  conditions:
  - lastTransitionTime: "2024-01-01T00:00:00Z"
    reason: Available
    status: "True"
    type: Ready
```
Now you could package and publish your function, functions are packed using OCI format, you can read more about at the [official docs](https://docs.crossplane.io/latest/guides/write-a-composition-function-in-python/).
