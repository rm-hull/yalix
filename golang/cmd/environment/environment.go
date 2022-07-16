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
	stackDepth  int
}

func MakeEnv[T any]() Env[T] {
	return Env[T]{
		localStack:  make([]stackEntry[T], 0),
		globalFrame: make(map[string]T),
		stackDepth:  0,
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
		stackDepth:  env.stackDepth,
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

// Traverses the local stack and sets the first instance of name with value
func (env Env[T]) SetLocal(name string, value T) error {
	last := len(env.localStack) - 1
	for idx := range env.localStack {
		if env.localStack[last-idx].name == name {
			env.localStack[last-idx].value = value
			return nil
		}
	}
	return errors.Errorf("assignment disallowed: '%s' is unbound in local environment", name)
}

func (env Env[T]) Includes(name string) bool {
	if _, ok := env.globalFrame[name]; ok {
		return true
	}

	for _, stackEntry := range env.localStack {
		if stackEntry.name == name {
			return true
		}
	}

	return false
}

func (env Env[T]) StackDepth() int {
	return env.stackDepth
}
