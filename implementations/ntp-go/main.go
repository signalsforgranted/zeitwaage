package main

import (
    "flag"
    "fmt"
    "os"
    "time"
    "github.com/beevik/ntp"
)

const defaultNtpPort = 1123
const defaultTimeout = 3

func main() {

        var (
			mode    string
			host    string
			port    int
			timeoutSecs int
        )

        flag.StringVar(&mode, "mode", "client", `mode of operation: "client" or "server"`)
        flag.StringVar(&host, "host", "localhost", "hostname")
        flag.IntVar(&port, "port", defaultNtpPort, "NTP port number")
        flag.IntVar(&timeoutSecs, "timeout", defaultTimeout, "timeout in seconds (1-30, default 3)")
		flag.Parse()

        if mode != "client" && mode != "server" {
			fmt.Fprintf(os.Stderr, "invalid -mode %q: must either be \"client\" or \"server\"\n", mode)
			os.Exit(1)
        }

        if timeoutSecs < 1 || timeoutSecs > 30 {
			fmt.Fprintf(os.Stderr, "Timeout out of range!")
			os.Exit(1)
        }

        timeout := time.Duration(timeoutSecs) * time.Second
        options := ntp.QueryOptions{ Timeout: timeout }
        time, err := ntp.QueryWithOptions(fmt.Sprintf("%s:%d", host, port), options)

        if err != nil {
			fmt.Fprintf(os.Stderr, "Query failed?")
			os.Exit(1)
        }

        fmt.Printf("%#v\n", time)

}