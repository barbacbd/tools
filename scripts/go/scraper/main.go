package main

import (
	"encoding/xml"
    "fmt"
    "io"
    "io/ioutil"
    "log"
    "net/http"
    "net/url"
    "os"
    "strings"
)

const (
	NOAASourcesURL = "https://www.ndbc.noaa.gov/kml/marineobs_as_kml.php?sort=pgm"
)

var (
    fileName    string
    fullURLFile string
)

type XMLDoc struct {
	Sources []Source `xml:"Document>Folder>Folder"`
}

type Source struct {
	// Name of the Source corresponding to Source Type
	Name string `json:"name" xml:"name"`
	// Description for the Source
	Description string `json:"description,omitempty" xml:"description"`

	// Placemarks are the xml version of the Buoy information. These
	// require additional parsing, so they are NOT interchangeable with
	// the Buoy Structs
	Placemarks []Placemark `xml:"Placemark"`
}

// type Folder struct {
// 	Name string `xml:"name"`
// 	Description string `xml:"description"`
// 	Placemarks []Placemark `xml:"Placemark"`
// }

type Placemark struct {
	Name string `xml:"name"`
	Description string `xml:"description"`
	Placement Point `xml:"LookAt"`
}

// type LookAt struct {
// 	Latitude float64 `xml:"latitude"`
// 	Longitude float64 `xml:"longitude"`
// 	Altitude float64 `xml:"altitude"`
// 	Range float64 `xml:"range"`
// }

type Point struct {
	// Latitude degrees for the world coordinates
	Latitude float64 `json:"latitude,omitempty" xml:"latitude"`

	// Longitude degrees for the world coordinates
	Longitude float64 `json:"longitude,omitempty" xml:"longitude"`

	// Altitude in meters above sea level. Negative values
	// are considered to be depth.
	Altitude float64 `json:"altitude,omitempty" xml:"altitude"`
}
 
func main() {
 
    // Build fileName from fullPath
    fileURL, err := url.Parse(NOAASourcesURL)
    if err != nil {
        log.Fatal(err)
    }
    path := fileURL.Path
    segments := strings.Split(path, "/")
    fileName = segments[len(segments)-1]
 
    // Create blank file
    file, err := os.Create(fileName)
    if err != nil {
        log.Fatal(err)
    }
    client := http.Client{
        CheckRedirect: func(r *http.Request, via []*http.Request) error {
            r.URL.Opaque = r.URL.Path
            return nil
        },
    }
    // Put content on file
    resp, err := client.Get(NOAASourcesURL)
    if err != nil {
        log.Fatal(err)
    }
    defer resp.Body.Close()
 
    size, err := io.Copy(file, resp.Body)
 
    defer file.Close()
 
    fmt.Printf("Downloaded a file %s with size %d\n", fileName, size)

    xmlFile, _ := os.Open(fileName)
    defer xmlFile.Close()

    byteValue, _ := ioutil.ReadAll(xmlFile)
    var myXMLDoc XMLDoc
    xml.Unmarshal(byteValue, &myXMLDoc)

    for _, source := range myXMLDoc.Sources {
    	fmt.Println(source.Name)
    }

    // fmt.Println(myXMLDoc)

    if err := os.Remove(fileName); err != nil {
    	fmt.Println("Failed to remove file")
    }
 
}