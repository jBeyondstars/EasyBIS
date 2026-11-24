// Batch front end to the pinned WoWSims Go simulator. Each request is one
// physical loadout and activation policy, with the same starting random seed.
package main

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"runtime"
	"sync"

	"github.com/wowsims/forever/sim"
	"github.com/wowsims/forever/sim/core"
	"github.com/wowsims/forever/sim/core/proto"
	"google.golang.org/protobuf/encoding/protojson"
)

type trial struct {
	Request json.RawMessage
	Watch   []int32
}

type batch struct {
	Trials []trial
	Packs  []int
	Pet    string
	Mana   bool
}

type measurement struct {
	Damage           []float64
	PackDamage       []float64
	PackHits         []int
	Seconds          float64
	Casts            map[int32]float64
	PetDamage        float64
	ManaRestored     []float64 `json:",omitempty"`
	ManaRefillEvents []int32   `json:",omitempty"`
	Error            string    `json:",omitempty"`
}

func measure(job trial, packs []int, pet string, mana bool) (m measurement) {
	defer func() {
		if failure := recover(); failure != nil {
			m.Error = fmt.Sprint(failure)
		}
	}()
	req := new(proto.RaidSimRequest)
	if err := (protojson.UnmarshalOptions{DiscardUnknown: false}).Unmarshal(job.Request, req); err != nil {
		panic(err)
	}
	o := core.RunRaidSim(req)
	n := int(req.SimOptions.Iterations)
	if o.Error != nil || int(o.IterationsDone) != n || n < 2 {
		panic(fmt.Sprintf("incomplete route (%d/%d): %v", o.IterationsDone, n, o.Error))
	}
	targets := o.EncounterMetrics.Targets
	dps := o.RaidMetrics.Dps.AllValues
	timer := targets[0].Threat.AllValues // The encounter emits one unit of threat per run.
	if len(dps) != n || len(timer) != n {
		panic("missing per-iteration route samples")
	}
	m.Damage = make([]float64, n)
	m.PackDamage = make([]float64, len(packs))
	m.PackHits = make([]int, len(packs))
	m.Casts = make(map[int32]float64)
	waves := make(map[int32]int)
	caps := make([]float64, len(packs))
	index := 0
	for wave, size := range packs {
		for k := 0; k < size; k++ {
			t := targets[index]
			if len(t.Dtps.AllValues) != n {
				panic("missing per-target damage samples")
			}
			waves[t.UnitIndex] = wave
			caps[wave] += req.Encounter.Targets[index].Stats[proto.Stat_StatHealth]
			index++
		}
	}
	if len(targets) != index || len(waves) != index {
		panic("unexpected route targets")
	}
	for i, rate := range dps {
		if !(timer[i] > 0) || math.IsInf(timer[i], 0) {
			panic("invalid end-of-route marker")
		}
		seconds := 1 / timer[i]
		if seconds >= req.Encounter.Duration {
			panic("dungeon timed out before the final enemy died")
		}
		m.Seconds += seconds / float64(n)
		damage := rate * seconds
		if !(damage > 0) || math.IsInf(damage, 0) {
			panic("invalid route damage")
		}
		m.Damage[i] = damage
		index = 0
		sum := 0.0
		for wave, size := range packs {
			group := 0.0
			for k := 0; k < size; k++ {
				group += targets[index].Dtps.AllValues[i] * seconds
				index++
			}
			if group > 0 {
				m.PackHits[wave]++
			}
			if group < 0 || group > caps[wave]+0.001 {
				panic("credited damage exceeds enemy hit points")
			}
			m.PackDamage[wave] += group / float64(n)
			sum += group
		}
		if math.Abs(sum-damage) > 0.001 {
			panic(fmt.Sprintf("player/pet damage %.6f differs from enemy damage %.6f", damage, sum))
		}
	}
	if math.Abs(m.Seconds-o.AvgIterationDuration) > 1e-6 {
		panic("individual completion times disagree with the native mean")
	}
	player := o.RaidMetrics.Parties[0].Players[0]
	if mana {
		m.ManaRestored = make([]float64, len(packs)-1)
		m.ManaRefillEvents = make([]int32, len(packs)-1)
	}
	for _, resource := range player.Resources {
		if resource.Id.GetSpellId() != 900071 {
			continue
		}
		transition := int(resource.Id.Tag) - 2
		if !mana || transition < 0 || transition >= len(m.ManaRestored) ||
			resource.Type != proto.ResourceType_ResourceTypeMana || int(resource.Events) != n ||
			m.ManaRefillEvents[transition] != 0 || !(resource.Gain > 0) ||
			!(resource.ActualGain >= 0 && resource.ActualGain <= resource.Gain+0.001) {
			panic("invalid between-pull mana refill")
		}
		m.ManaRestored[transition] = resource.ActualGain / float64(n)
		m.ManaRefillEvents[transition] = resource.Events
	}
	for _, events := range m.ManaRefillEvents {
		if int(events) != n {
			panic("a mana user started a pull without the required refill")
		}
	}
	for _, iid := range job.Watch {
		m.Casts[iid] = 0
		for _, action := range player.Actions {
			if action.Id.GetItemId() == iid {
				for _, t := range action.Targets {
					m.Casts[iid] += float64(t.Casts) / float64(n)
				}
			}
		}
	}
	actionDamage := make([]float64, len(packs))
	for _, unit := range append([]*proto.UnitMetrics{player}, player.Pets...) {
		for _, action := range unit.Actions {
			for _, t := range action.Targets {
				if wave, ok := waves[t.UnitIndex]; ok {
					actionDamage[wave] += t.Damage / float64(n)
					if unit != player && unit.Name == pet {
						m.PetDamage += t.Damage / float64(n)
					}
				}
			}
		}
	}
	for wave, total := range actionDamage {
		if !(total > 0) || math.Abs(total-m.PackDamage[wave]) > 0.001 {
			panic(fmt.Sprintf("wave %d has %.6f action damage and %.6f sampled damage", wave+1, total, m.PackDamage[wave]))
		}
	}
	if pet != "" && m.PetDamage <= 0 {
		panic("required pet dealt no damage: " + pet)
	}
	return
}

func main() {
	sim.RegisterAll()
	var jobs batch
	if err := json.NewDecoder(os.Stdin).Decode(&jobs); err != nil {
		panic(err)
	}
	queue := make(chan int)
	results := make([]measurement, len(jobs.Trials))
	var workers sync.WaitGroup
	for i := 0; i < runtime.GOMAXPROCS(0); i++ {
		workers.Add(1)
		go func() {
			defer workers.Done()
			for index := range queue {
				results[index] = measure(jobs.Trials[index], jobs.Packs, jobs.Pet, jobs.Mana)
			}
		}()
	}
	for index := range jobs.Trials {
		queue <- index
	}
	close(queue)
	workers.Wait()
	if err := json.NewEncoder(os.Stdout).Encode(results); err != nil {
		panic(err)
	}
}
