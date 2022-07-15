package interpreter

import "yalix/cmd/environment"

type Primitive[T any] interface {
	Eval(env environment.Env[T]) (any, error)
	Apply(env environment.Env[T], caller any) (any, error)
}
