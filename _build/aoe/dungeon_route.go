// Added to the pinned WoWSims core by aoe_encounter.write_overlay.
package core

import (
	"fmt"
	"time"

	"github.com/wowsims/forever/sim/core/proto"
)

const routeFirstID = 900010
const routeGroupSpell = 900070
const routeDrinkSpell = 900071
const routePulse = 100 * time.Millisecond

func init() {
	for index := 0; index < 12; index++ {
		AddPresetTarget(&PresetTarget{
			PathPrefix: "EasyBIS",
			Config:     &proto.Target{Id: int32(routeFirstID + index), Name: fmt.Sprintf("Dungeon route target %d", index+1)},
			AI:         func() TargetAI { return &routeEnemy{} },
		})
	}
}

type routeEnemy struct {
	unit        *Target
	pack        int
	groupDPS    float64
	travel      time.Duration
	groupDamage *ResourceMetrics
	spawnedAt   time.Duration
	dead        bool
	drink       bool
	drinkers    []routeDrinker
}

type routeDrinker struct {
	player  *Character
	metrics [2]*ResourceMetrics
}

func (e *routeEnemy) Initialize(target *Target, config *proto.Target) {
	e.unit = target
	target.Label = config.Name
	e.pack = int(config.TargetInputs[0].NumberValue)
	e.groupDPS = config.TargetInputs[1].NumberValue
	e.travel = DurationFromSeconds(config.TargetInputs[2].NumberValue)
	e.drink = config.TargetInputs[3].NumberValue == 1
	target.EnableHealthBar()
	e.groupDamage = target.NewHealthMetrics(ActionID{SpellID: routeGroupSpell})
	target.Schedule = e
}

func (e *routeEnemy) Reset(sim *Simulation) {
	e.dead = false
	e.spawnedAt = NeverExpires
	e.unit.executeAt35, e.unit.executeAt25, e.unit.executeAt20 = NeverExpires, NeverExpires, NeverExpires
	sim.Encounter.updateNextExecuteDuration(sim)
	if e.pack == 1 {
		e.spawnedAt = 0
		if !e.unit.IsEnabled() {
			e.unit.Enable(sim)
		}
	} else {
		e.unit.Disable(sim, true)
	}
	if e.unit.Index == 0 {
		if e.drink {
			if e.drinkers == nil {
				e.drinkers = []routeDrinker{}
				for _, party := range sim.Raid.Parties {
					for _, agent := range party.Players {
						player := agent.GetCharacter()
						if !player.HasManaBar() {
							continue
						}
						drinker := routeDrinker{player: player}
						for index := range drinker.metrics {
							metrics := player.NewManaMetrics(ActionID{SpellID: routeDrinkSpell, Tag: int32(index + 2)})
							metrics.NoThreat = true
							drinker.metrics[index] = metrics
						}
						e.drinkers = append(e.drinkers, drinker)
					}
				}
			}
			// Target reset precedes player reset. Inspect initial mana after both resets,
			// before any pull action; the first pack never grants a drink.
			sim.AddPendingAction(NewDelayedAction(DelayedActionOptions{DoAt: 0, Priority: ActionPriorityPrePull + 1000,
				OnAction: func(sim *Simulation) { e.startPackWithMana(sim, 1) },
			}))
		}
		e.schedulePulse(sim)
	}
}

func (e *routeEnemy) startPackWithMana(sim *Simulation, pack int) {
	for _, drinker := range e.drinkers {
		player := drinker.player
		capacity := player.MaxMana()
		if pack > 1 {
			// AddMana clips to the player's current maximum, including temporary effects.
			// The requested gain records that maximum; actual gain records the deficit.
			player.AddMana(sim, capacity, drinker.metrics[pack-2])
		}
		if player.CurrentMana() != capacity {
			panic("Dungeon pull did not start at full mana")
		}
		if sim.Log != nil {
			player.Log(sim, "Dungeon pack %d starts at full mana: %.3f / %.3f", pack, player.CurrentMana(), capacity)
		}
	}
}

func (e *routeEnemy) ExecuteCustomRotation(sim *Simulation) {
	e.unit.ExtendGCDUntil(sim, sim.CurrentTime+BossGCD)
}

func (e *routeEnemy) NextActiveAt(*Simulation) time.Duration {
	if e.dead {
		return NeverExpires
	}
	return e.spawnedAt
}

// The APL sees an estimate of time left, based on this target's observed rate of
// health loss since its pull. In the absence of damage use the group's known rate.
func (e *routeEnemy) DiesAt(sim *Simulation) time.Duration {
	if !e.unit.IsEnabled() || e.dead {
		return NeverExpires
	}
	rate := e.groupDPS / float64(max(1, len(sim.Encounter.ActiveTargets)))
	elapsed := (sim.CurrentTime - e.spawnedAt).Seconds()
	if elapsed > 0 {
		rate = max(rate, (e.unit.MaxHealth()-e.unit.CurrentHealth())/elapsed)
	}
	return sim.CurrentTime + DurationFromSeconds(e.unit.CurrentHealth()/rate)
}

// Called at damage delivery, after missile travel and before spell metrics/procs.
// Delaying the removal until the current event ends leaves AoE target iteration
// safe; further hits on a killed target are discarded immediately.
func routeImpact(sim *Simulation, spell *Spell, result *SpellResult) bool {
	if result.Target.Type != EnemyUnit {
		return true
	}
	e, ok := sim.Encounter.AllTargets[result.Target.Index].AI.(*routeEnemy)
	if !ok {
		return true
	}
	if !e.unit.IsEnabled() || e.dead {
		return false
	}
	if result.Damage > 0 {
		raw := result.Damage
		result.Damage = min(raw, e.unit.CurrentHealth())
		result.Threat *= result.Damage / raw
		e.spend(sim, result.Damage, e.unit.DamageTakenHealthMetrics, 1)
	}
	return true
}

func (e *routeEnemy) spend(sim *Simulation, amount float64, metrics *ResourceMetrics, killShare float64) {
	e.unit.SpendHealth(sim, amount, metrics)
	switch percent := e.unit.CurrentHealthPercent(); {
	case percent <= 0.20:
		e.unit.executePhase = 20
	case percent <= 0.25:
		e.unit.executePhase = 25
	case percent <= 0.35:
		e.unit.executePhase = 35
	}
	if e.unit.CurrentHealth() > 0 {
		return
	}
	e.dead = true
	sim.AddPendingAction(NewDelayedAction(DelayedActionOptions{DoAt: sim.CurrentTime, Priority: ActionPriorityDOT,
		OnAction: func(sim *Simulation) { e.finishEnemy(sim, killShare) },
	}))
}

func (e *routeEnemy) finishEnemy(sim *Simulation, killShare float64) {
	e.unit.Die(sim, killShare)
	if len(sim.Encounter.ActiveTargets) != 0 {
		return
	}
	if e.pack == 3 {
		// No enemy attacks or generates threat. One marker over the measured duration
		// gives the duration of each individual sample in target 0's threat distribution.
		sim.Encounter.AllTargets[0].Metrics.threat.Total = 1
		sim.Duration = sim.CurrentTime
		sim.endOfCombatDuration = sim.CurrentTime
		return
	}
	when := sim.CurrentTime + e.travel
	for _, target := range sim.Encounter.AllTargets {
		next := target.AI.(*routeEnemy)
		if next.pack == e.pack+1 {
			next.spawnedAt = when
		}
	}
	sim.AddPendingAction(NewDelayedAction(DelayedActionOptions{DoAt: when, Priority: ActionPriorityDOT,
		OnAction: func(sim *Simulation) {
			sim.Encounter.AllTargets[0].AI.(*routeEnemy).startPackWithMana(sim, e.pack+1)
			for _, target := range sim.Encounter.AllTargets {
				if target.AI.(*routeEnemy).pack == e.pack+1 {
					target.Enable(sim)
				}
			}
			e.schedulePulse(sim)
		},
	}))
}

func (e *routeEnemy) schedulePulse(sim *Simulation) {
	sim.AddPendingAction(NewDelayedAction(DelayedActionOptions{DoAt: sim.CurrentTime + routePulse,
		Priority: ActionPriorityLow, OnAction: func(sim *Simulation) {
			// A pulse left from a finished pack during travel must not start another clock.
			if len(sim.Encounter.ActiveTargets) == 0 {
				return
			}
			budget := e.groupDPS * routePulse.Seconds()
			for budget > 0.000001 {
				count := 0
				for _, t := range sim.Encounter.ActiveTargets {
					if !t.AI.(*routeEnemy).dead {
						count++
					}
				}
				if count == 0 {
					return
				}
				share := budget / float64(count)
				for _, target := range sim.Encounter.ActiveTargets {
					m := target.AI.(*routeEnemy)
					if !m.dead {
						amount := min(share, target.CurrentHealth())
						budget -= amount
						m.spend(sim, amount, m.groupDamage, 0)
					}
				}
			}
			e.schedulePulse(sim)
		},
	}))
}
