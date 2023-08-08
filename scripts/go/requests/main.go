package main

import (
    "context"
    "fmt"
    // api "google.golang.org/api/iam/v1"
    api "google.golang.org/api/cloudresourcemanager/v1"
)


func main() {
    ctx := context.Background()

    service, err := api.NewService(ctx)
    if err != nil {
        fmt.Println(err.Error())
        return
    }

    projectsService := api.NewProjectsService(service)

    rb := &api.TestIamPermissionsRequest{
        Permissions: []string{
            "compute.firewalls.get",
        },
    }

    resource := "openshift-dev-installer"
    response, err := projectsService.TestIamPermissions(resource, rb).Context(ctx).Do()
    if err != nil {
        fmt.Println(err.Error())
        return
    }

    fmt.Printf("%+v\n", response)

    for _, perm := range response.Permissions {
        fmt.Println(perm)
    }
}