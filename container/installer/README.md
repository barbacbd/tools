# Installer Container Documentation

The script `generate.py` will generate the necessary file for creating a docker image.

The output files will reside in `./openshift-installer-data`

```bash
python3 generate.py <args>

cd openshift-installer-data

podman build . -t $USER:latest
```

# Arguments
The following are the arguments that can be supplied to the generate script.

## Required

`ssh_key'` - File where the users public key can be found
`seecrets` - File where all secrets credential information can be found.

## Optional

`-p`, `--platform` - Supported cloud platform to configure.
- Accepted = 'aws', 'gcp'
- Default = 'aws'

`-r`, `--region` -Platform region to use for configuration.
- Default=None

`--aws_profile` - Only appliable to aws, AWS Profile Settings, found in aws config.
- Default = 'openshift-dev'

`--google_creds` - Only appliable to gcp, GCP App Creds file.
- Default = '~/.gcp/gcp-key.json'

`--os_image_name` - path/name of the Openshift image to use.
- Default = 'quay.io/openshift-release-dev/ocp-release:4.10.10.x86_64'

`--custom_image_name` - name of the image that will be created from the dockerfile.
- Default = 'installer-wwt'

`--custom_image_tag` - tag for the image that will be created from the dockerfile.
- Default = 'latest'

`--installer_dir` - Base directory for the local openshift installer code.
- Default = '~/dev/installer'


# Supported Platforms

- aws
- gcp

