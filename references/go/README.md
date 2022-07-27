# GO installation

For a reference the [go docs](https://go.dev/doc/install) are provided.

## Installing go.

Select the operating system in the `GO Install` section and follow the directions.

## Intializing a project

The user should run `go mod init` to initialize the project.

**Note**: _If the user wants to initialize a project on github, run go mod init github.com/{user}/{project}_.

## Get the dependencies

Run `go mod tidy` to grab the dependencies. This can also be used to update the dependencies when the project requires dependency updates.

_If the project has a vendor directory (golang >= 1.15), run `go mod vendor` to update the vendor packages_.


## Add to path

Select the operating system in the `GO Install` section and follow the directions.