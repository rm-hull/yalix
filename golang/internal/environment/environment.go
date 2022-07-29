package environment

import (
	"sync/atomic"

	"github.com/pkg/errors"
)

type stackEntry struct {
	name  string
	value any
}

type Env struct {
	localStack  []stackEntry
	globalFrame map[string]any
	stackDepth  int
}

func MakeEnv() Env {
	return Env{
		localStack:  make([]stackEntry, 0),
		globalFrame: make(map[string]any),
		stackDepth:  0,
	}
}

// Extend the local stack with the given name/value.
// Note 2: global frame is shared across extended environments.
func (env Env) Extend(name string, value any) Env {
	// Prune any shadow bindings, before pushing new name/value
	var newStack = make([]stackEntry, 0)
	for _, entry := range env.localStack {
		if entry.name != name {
			newStack = append(newStack, entry)
		}
	}
	newStack = append(newStack, stackEntry{name, value})

	return Env{
		localStack:  newStack,
		globalFrame: env.globalFrame,
		stackDepth:  env.stackDepth,
	}
}

// Adds a new global definition, and evaluates it according to self
func (env *Env) SetGlobal(name string, value any) {
	env.globalFrame[name] = value
}

// Look in the local stack first for the named item, then try the global frame
func (env *Env) Get(name string) (any, error) {
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
func (env *Env) SetLocal(name string, value any) error {
	last := len(env.localStack) - 1
	for idx := range env.localStack {
		if env.localStack[last-idx].name == name {
			env.localStack[last-idx].value = value
			return nil
		}
	}
	return errors.Errorf("assignment disallowed: '%s' is unbound in local environment", name)
}

func (env *Env) Includes(name string) bool {
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

func (env *Env) StackDepth() int {
	return env.stackDepth
}

func (env *Env) IncreaseStackDepth() {
	env.stackDepth += 1
}

var id uint32

func NextId() uint {
	return uint(atomic.AddUint32(&id, 1))
}
