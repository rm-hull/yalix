package environment

import (
	"github.com/pkg/errors"
)

type stackEntry[T any] struct {
	name  string
	value T
}

type Env[T any] struct {
	localStack  []stackEntry[T]
	globalFrame map[string]T
}

func MakeEnv[T any]() Env[T] {
	return Env[T]{
		localStack:  make([]stackEntry[T], 0),
		globalFrame: make(map[string]T),
	}
}

// Extend the local stack with the given name/value.
// Note 2: global frame is shared across extended environments.
func (env Env[T]) Extend(name string, value T) Env[T] {
	// Prune any shadow bindings, before pushing new name/value
	var newStack = make([]stackEntry[T], 0)
	for _, entry := range env.localStack {
		if entry.name != name {
			newStack = append(newStack, entry)
		}
	}
	newStack = append(newStack, stackEntry[T]{name, value})

	return Env[T]{
		localStack:  newStack,
		globalFrame: env.globalFrame,
	}
}

// Adds a new global definition, and evaluates it according to self
func (env Env[T]) SetGlobal(name string, value T) {
	env.globalFrame[name] = value
}

// Look in the local stack first for the named item, then try the global frame
func (env Env[T]) Get(name string) (T, error) {
	last := len(env.localStack) - 1
	for idx := range env.localStack {
		if env.localStack[last-idx].name == name {
			return env.localStack[last-idx].value, nil
		}
	}

	value, ok := env.globalFrame[name]
	if !ok {
		return value, errors.Errorf("'%s' is unbound in environment", name)
	}

	return value, nil
}
