package interpreter

import (
	"errors"
	"yalix/cmd/environment"
)

type atom struct {
	Primitive[any]
	value any
}

func Atom[T any](value T) atom {
	return atom{value: value}
}

func (a atom) Eval(env environment.Env[any]) (any, error) {
	return a.value, nil
}

func (a atom) Apply(env environment.Env[any], caller Caller) (any, error) {
	return nil, errors.New("cannot invoke with: 'Atom'")
}

func (a atom) QuotedForm(env environment.Env[any]) (any, error) {
	return a.Eval(env)
}
