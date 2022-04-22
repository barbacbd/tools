# Installer Container Documentation

The script `generate.py` will generate the necessary file for creating a docker image.

The following is the output when the command in line 1 is executed.

```
[$USER@$USER installer]$ python3 generate.py 
Removing all data from openshift-installer-data
Execute the following command:

cd openshift-installer-data && podman build . -t <image_name>:<image_tag>
```

The output files will reside in `./openshift-installer-data`. The user can copy and paste
the final line of the output to create the image.

The following should provide a look at your new image.

```bash
podman image ls
```

To enter the image go to `openshift-installer-data` and execute `connect.sh`.

To run the installer with the auto generated config, execute the script `install.sh` from
a running container. The file resides in `/`.


# YAML Configuration


# Supported Platforms

- aws
- gcp

