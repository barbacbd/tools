# Azure Setup

## Installing Azure CLI

Import the microsoft repo key

```bash
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
```

Download the repo

```bash
sudo dnf install -y https://packages.microsoft.com/config/rhel/8/packages-microsoft-prod.rpm
```

Install the CLI (you can also install specific versions).

```bash
sudo dnf install azure-cli
```

**Note**: _Installation assume RHEL/Fedora Distribution_.


## Start using the CLI

az login

**Note**: _This will bring up the azure site and ask for your login_.

**Note**: _You should see the output on the screen. The same information can be found int `~/.azure`_. 


## Create the credentials

Find your subscription ID in `~/.azure`.

```bash
cd ~/.azure;
grep -r subscription *
```

You should see a uuid formatted string. Find this string and use it in the next step.


```bash
az ad sp create-for-rbac --role Owner --scopes /subscription/{SUBSCRIPTION_ID} --name {USERNAME}-{PURPOSE}
```

In the snippet above:
- SUBSCRIPTION_ID - ID foudn in the first step above
- USERNAME - Main name of the service principal
- PURPOSE - What project you want this attached to

**Note**: _The service principal that I used was `barbacbd-installer`_.
**Note**: _In old versions the `--scopes` was not required, now it is_.

The output should be something similar to:

```json
{
  "appId": {uuid},
  "displayName": "barbacbd-installer",
  "password": {password},
  "tenant": {uuid}
}
```

## Installing cluster

Follow the snippet below inputting data from above examples

```bash
$ openshift-install create cluster
? SSH Public Key /home/{USER}/.ssh/{ssh-key}.pub
? Platform azure
? azure subscription id {SUBSCRIPTION_ID}
? azure tenant id {tenant}
? azure service principal client id {appId}
? azure service principal client secret [? for help] {password}
INFO Saving user credentials to "/home/{USER}/.azure/osServicePrincipal.json" 
INFO Credentials loaded from file "/home/{USER}/.azure/osServicePrincipal.json"
```

**Note**: _Assumes that `openshift-installer` is in path_.

