// Encounter used only by the offline WoWSims CLI, added with go build -overlay.
package core

import (
	"time"

	"github.com/wowsims/forever/sim/core/proto"
)

func init() {
	AddPresetTarget(&PresetTarget{
		PathPrefix: "EasyBIS",
		Config: &proto.Target{
			Id: 900001, Name: "Dungeon pack member", Level: 60, TankIndex: -1,
			TargetInputs: []*proto.TargetInput{
				{Label: "Spawn time (s)", InputType: proto.InputType_Number, NumberValue: 0},
				{Label: "Despawn time (s)", InputType: proto.InputType_Number, NumberValue: 15},
			},
		},
		AI: func() TargetAI { return &packMember{} },
	})
}

type packMember struct {
	target     *Target
	start, end time.Duration
}

func (m *packMember) Initialize(target *Target, config *proto.Target) {
	m.target = target
	m.start = DurationFromSeconds(config.TargetInputs[0].NumberValue)
	m.end = DurationFromSeconds(config.TargetInputs[1].NumberValue)
	target.Schedule = m
}

func (m *packMember) NextActiveAt(sim *Simulation) time.Duration {
	if sim.CurrentTime <= m.start {
		return m.start
	}
	return NeverExpires
}

func (m *packMember) DiesAt(*Simulation) time.Duration { return m.end }

func (m *packMember) Reset(sim *Simulation) {
	// A fresh pack crosses execute thresholds during its own lifetime.
	duration := float64(m.end - m.start)
	m.target.executeAt35 = m.start + time.Duration((1-sim.Encounter.ExecuteProportion_35)*duration)
	m.target.executeAt20 = m.start + time.Duration((1-sim.Encounter.ExecuteProportion_20)*duration)
	m.target.executeAt25 = m.target.executeAt35 + (m.target.executeAt20-m.target.executeAt35)*2/3
	sim.Encounter.updateNextExecuteDuration(sim)
	if m.start > 0 {
		m.target.Disable(sim, true)
		sim.AddPendingAction(NewDelayedAction(DelayedActionOptions{
			DoAt: m.start, Priority: ActionPriorityDOT, OnAction: m.target.Enable,
		}))
	} else if !m.target.IsEnabled() {
		m.target.Enable(sim)
	}
	sim.AddPendingAction(NewDelayedAction(DelayedActionOptions{
		DoAt: m.end, Priority: ActionPriorityDOT,
		OnAction: func(sim *Simulation) { m.target.Die(sim, 0) },
	}))
}

func (m *packMember) ExecuteCustomRotation(sim *Simulation) {
	m.target.ExtendGCDUntil(sim, sim.CurrentTime+BossGCD)
}
