# Crossplane tutorial

This tutorial introduces Crossplane in a local environment with the most important topics and exposing some pain points.  
After this, you should be able to start in any crossplane environment to deploy infrastructure and create your own compositions and functions.  
You just need a Linux based workstation, I tested it in WSL2 Ubuntu distribution.

# Prerequisites
In order to start this lab, ensure you have the following dependencies:
* [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download) or similar
* [kubectl](https://v1-32.docs.kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm cli](https://helm.sh/docs/intro/install/)
* [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [localstack](https://docs.localstack.cloud/aws/getting-started/installation/)
* [crossplane cli](https://docs.crossplane.io/latest/cli/)
* [upbound cli](https://docs.upbound.io/manuals/cli/overview/)

# Setting up
## Kubernetes
Start a minikube instance and validate it:
```bash
$ minikube start
😄  minikube v1.37.0 on Ubuntu 24.04 (kvm/amd64)
✨  Automatically selected the docker driver
📌  Using Docker driver with root privileges
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image v0.0.48 ...
🔥  Creating docker container (CPUs=2, Memory=3900MB) ...
🐳  Preparing Kubernetes v1.34.0 on Docker 28.4.0 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default

$ kubectl config current-context
minikube

$ kubectl cluster-info
Kubernetes control plane is running at https://127.0.0.1:32771
CoreDNS is running at https://127.0.0.1:32771/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

$ kubectl get nodes
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   90s   v1.34.0
```

## Localstack and AWS CLI
Now, install localstack by adding the helm repo if not present yet:
```bash
$ helm repo add localstack-repo https://helm.localstack.cloud

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "localstack-repo" chart repository
Update Complete. ⎈Happy Helming!⎈
```
and install it on the new minikube cluster:
```bash
$ helm upgrade --install localstack localstack-repo/localstack --namespace localstack --create-namespace

Release "localstack" does not exist. Installing it now.
NAME: localstack
LAST DEPLOYED: Tue Oct 21 15:53:54 2025
NAMESPACE: localstack
STATUS: deployed
REVISION: 1

$ kubectl -n localstack get pods
NAME                          READY   STATUS    RESTARTS   AGE
localstack-84bf744796-jxz8j   1/1     Running   0          68s
```

In order to run aws cli against localstack, open another console and run a port forward to the localstack endpoint:
```bash
$ kubectl port-forward svc/localstack 4566:4566 -n localstack
Forwarding from 127.0.0.1:4566 -> 4566
Forwarding from [::1]:4566 -> 4566
```
In your `.bashrc` or `.zshrc` set the following code at the end:
```bash
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy
alias awslocal='aws --endpoint-url=http://localhost:4566 --region=us-east-1 --no-sign-request'
```

Now you should be able to connect and get some dummy data, like:
```bash
$ awslocal sts get-caller-identity

{
    "UserId": "AKIAIOSFODNN7EXAMPLE",
    "Account": "000000000000",
    "Arn": "arn:aws:iam::000000000000:root"
}
```

## Crossplane
Install the UXP crossplane version by typing:
```bash
$ up uxp install
  ✓   Installing UXP
  🙌  UXP 2.0.2-up.4 installed
 INFO  If you have a UXP license, apply it now with `up uxp license apply`.
```
Don't worry about the license INFO message, we don't need a license at all, I will explain this part later.  
By now, verify everything is running:
```bash
$ kubectl -n crossplane-system get pods
NAME                                          READY   STATUS    RESTARTS        AGE
crossplane-apollo-57c94c4d78-k72s9            3/3     Running   2 (3m44s ago)   4m11s
crossplane-d969b8bcb-w5ptr                    1/1     Running   0               4m11s
crossplane-rbac-manager-79d448966b-6nncb      1/1     Running   0               4m11s
upbound-controller-manager-86c846d988-bhv5z   1/1     Running   0               4m11s
webui-5fcbfbc675-rtbmm                        1/1     Running   0               4m11s
```

### Crossplane vs Upbound and UXP
#### The crossplane distro
Crossplane is the open source community driven project while upbound is the company upstream. You can install the community one through helm charts or the Upbound UXP (Upbound.Cross.Plane.) free version and upgrade to PRO anytime by applying the license that brings some AI driven functionality.  
Also, the free UXP brings some nice tools like a WEB UI you can access by opening a new term and type:
``` bash
$ kubectl port-forward svc/webui 8080:80 -n crossplane-system
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
```
Then open http://localhost:8080/ in a new browser.  

#### Providers
Notice you will also find a sort of providers that implements the terraform providers for crossplane, the crossplane mantained providers, which are mostly discontinued and the Upbound's providers which are generated from the original provider with [upjet](https://github.com/crossplane/upjet), that compiles the provider into a valid crossplane equivalent one. Every provider can be retrieved from a repository so we won't need to compile anything at all.  
Example of AWS ELB provider by crossplane and upboud:
* Crossplane: https://marketplace.upbound.io/providers/crossplane-contrib/provider-aws/v0.56.0
* Upbound: https://marketplace.upbound.io/providers/upbound/provider-aws-elb/v2.1.1

It's important to be aware anytime on which provider are we working and it's spec, as note how they differ in the `listeners` (crossplane) and `listener` (upbound).

# Start the tutorial
Now you are ready to start the tutorial [here](docs/), have a coffee, you earned it! ☕
