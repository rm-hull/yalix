package interpreter

import "yalix/internal/environment"

type Primitive[T any] interface {
	Eval(env environment.Env[T]) (any, error)
	Apply(env environment.Env[T], caller Caller) (any, error)
	QuotedForm(env environment.Env[T]) (any, error)
	Repr() string
}
