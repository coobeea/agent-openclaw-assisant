// Package kernel provides factory for creating kernel adapters
package kernel

import (
	"fmt"
	"sync"
)

// KernelFactory is responsible for creating kernel adapters based on configuration
type KernelFactory struct {
	// registry maps kernel types to their constructor functions
	registry map[KernelType]KernelConstructor

	// mu protects concurrent access to registry
	mu sync.RWMutex
}

// KernelConstructor is a function that creates a new kernel instance
type KernelConstructor func() KernelInterface

// globalFactory is the singleton factory instance
var (
	globalFactory     *KernelFactory
	globalFactoryOnce sync.Once
)

// GetFactory returns the global kernel factory instance
func GetFactory() *KernelFactory {
	globalFactoryOnce.Do(func() {
		globalFactory = NewKernelFactory()
	})
	return globalFactory
}

// NewKernelFactory creates a new kernel factory
func NewKernelFactory() *KernelFactory {
	factory := &KernelFactory{
		registry: make(map[KernelType]KernelConstructor),
	}

	// Register built-in kernels
	// Import cycle prevention: adapters are registered dynamically
	// or we use init() in adapter packages

	return factory
}

// Register registers a kernel constructor with the factory
func (f *KernelFactory) Register(kernelType KernelType, constructor KernelConstructor) error {
	f.mu.Lock()
	defer f.mu.Unlock()

	if _, exists := f.registry[kernelType]; exists {
		return fmt.Errorf("kernel type %s is already registered", kernelType)
	}

	f.registry[kernelType] = constructor
	return nil
}

// Unregister removes a kernel constructor from the factory
func (f *KernelFactory) Unregister(kernelType KernelType) {
	f.mu.Lock()
	defer f.mu.Unlock()
	delete(f.registry, kernelType)
}

// CreateKernel creates a new kernel instance based on the provided configuration
func (f *KernelFactory) CreateKernel(config *KernelConfig) (KernelInterface, error) {
	// Validate configuration
	if err := config.Validate(); err != nil {
		return nil, fmt.Errorf("invalid kernel config: %w", err)
	}

	f.mu.RLock()
	constructor, exists := f.registry[config.Type]
	f.mu.RUnlock()

	if !exists {
		return nil, fmt.Errorf("kernel type '%s' is not registered. Available types: %v",
			config.Type, f.GetRegisteredTypes())
	}

	// Create kernel instance
	kernel := constructor()
	return kernel, nil
}

// GetRegisteredTypes returns a list of all registered kernel types
func (f *KernelFactory) GetRegisteredTypes() []KernelType {
	f.mu.RLock()
	defer f.mu.RUnlock()

	types := make([]KernelType, 0, len(f.registry))
	for t := range f.registry {
		types = append(types, t)
	}
	return types
}

// IsRegistered checks if a kernel type is registered
func (f *KernelFactory) IsRegistered(kernelType KernelType) bool {
	f.mu.RLock()
	defer f.mu.RUnlock()
	_, exists := f.registry[kernelType]
	return exists
}

// CreateKernelFromEnv creates a kernel from environment-based configuration
// This is a convenience function for common deployment scenarios
func CreateKernelFromEnv(kernelType KernelType, endpoint, authToken string) (KernelInterface, error) {
	var config *KernelConfig

	switch kernelType {
	case KernelTypeOpenClaw:
		config = DefaultOpenClawConfig(endpoint, authToken)
	case KernelTypeQwenPaw:
		config = DefaultQwenPawConfig(endpoint)
	default:
		return nil, fmt.Errorf("unknown kernel type: %s", kernelType)
	}

	return GetFactory().CreateKernel(config)
}

// MustCreateKernel creates a kernel or panics on error
// Use this only when kernel creation failure is unrecoverable
func MustCreateKernel(config *KernelConfig) KernelInterface {
	kernel, err := GetFactory().CreateKernel(config)
	if err != nil {
		panic(fmt.Sprintf("failed to create kernel: %v", err))
	}
	return kernel
}
