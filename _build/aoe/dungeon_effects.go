// Emit the complete native metrics for one of the serial trials in dungeon_batch.go.
package main

import (
	"io"
	"log"
	"os"

	"github.com/wowsims/forever/sim"
	"github.com/wowsims/forever/sim/core"
	"github.com/wowsims/forever/sim/core/proto"
	"google.golang.org/protobuf/encoding/protojson"
)

func main() {
	sim.RegisterAll()
	input, err := io.ReadAll(os.Stdin)
	if err != nil {
		log.Fatal(err)
	}
	request := new(proto.RaidSimRequest)
	if err := protojson.Unmarshal(input, request); err != nil {
		log.Fatal(err)
	}
	result, err := (protojson.MarshalOptions{EmitUnpopulated: true}).Marshal(core.RunRaidSim(request))
	if err != nil {
		log.Fatal(err)
	}
	if _, err := os.Stdout.Write(result); err != nil {
		log.Fatal(err)
	}
}
