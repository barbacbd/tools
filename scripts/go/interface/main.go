package main

import (
       "fmt"
       "encoding/json"
       "os"

       "github.com/pkg/errors"
)

type instanceAttribute struct {
     DNSName string `json:"dns_name"`
}

type instance struct {
     Attributes []*instanceAttribute `json:"attributes,omitempty"`
}

type resource struct {
	Module    string      `json:"module,omitempty"`
	Type      string      `json:"type,omitempty"`
	Name      string      `json:"name,omitempty"`
	Instances []*instance `json:"instances,omitempty"`
}

type tfstate struct {
     Resources []resource `json:"resources"`
}

func getTerraformFileData(filename string) (map[string]interface{}, error) {
	if _, err := os.Stat(filename); err != nil {
		return nil, errors.Wrapf(err, "could not find outputs file %q", filename)
	}

	outputsFile, err := os.ReadFile(filename)
	if err != nil {
		return nil, errors.Wrapf(err, "failed to read outputs file %q", filename)
	}

	outputs := map[string]interface{}{}
	if err := json.Unmarshal(outputsFile, &outputs); err != nil {
		return nil, errors.Wrapf(err, "could not unmarshal outputs file %q", filename)
	}

	return outputs, nil
}

func extractInstanceValues(r resource) []string {
	var dnsNames = []string{}
	for _, inst := range r.Instances {
	    fmt.Println(inst)
	    for _, attr := range inst.Attributes {
	        fmt.Println(attr.DNSName)
		dnsNames = append(dnsNames, attr.DNSName)
	    }
	}
	return dnsNames
}

func main() {
	fmt.Println("\n\nTHIS IS extractAWSLBAddresses -> AWS\n\n")

	tfdata, err := getTerraformFileData("cluster.tfvars.json")
	if err != nil {
		fmt.Printf("%q\n", err)
	}

	apiLBName, ok := tfdata["aws_lb_api_external_dns_name"]
	if !ok {
	   fmt.Println("failed to find external load balancer name")
	}

	apiIntLBName, ok := tfdata["aws_lb_api_internal_dns_name"]
	if !ok {
	   fmt.Println("failed to find internal load balancer name")
	}

	fmt.Printf("Internal Load Balancer DNS Name: %s\n", apiIntLBName)
	fmt.Printf("External Load Balancer DNS Name: %s\n", apiLBName)
}