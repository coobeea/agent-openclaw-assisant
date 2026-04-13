// Package adapters provides registration for all kernel adapters
package adapters

import (
	"openclaw-scheduler/internal/kernel"
)

func init() {
	// Register OpenClaw adapter
	if err := kernel.GetFactory().Register(kernel.KernelTypeOpenClaw, NewOpenClawAdapter); err != nil {
		panic("failed to register OpenClaw adapter: " + err.Error())
	}

	// Register QwenPaw adapter
	if err := kernel.GetFactory().Register(kernel.KernelTypeQwenPaw, NewQwenPawAdapter); err != nil {
		panic("failed to register QwenPaw adapter: " + err.Error())
	}
}
