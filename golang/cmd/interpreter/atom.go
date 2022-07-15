package interpreter

import "yalix/cmd/environment"

type atom[T any] struct {
	Primitive[T]
	value T
}

func Atom[T any](value T) atom[T] {
	return atom[T]{value: value}
}

func (a atom[T]) Eval(env environment.Env[T]) (T, error) {
	return a.value, nil
}
