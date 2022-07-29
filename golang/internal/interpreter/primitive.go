package interpreter

import "yalix/internal/environment"

type Primitive interface {
	Eval(env environment.Env) (any, error)
	Apply(env environment.Env, caller Caller) (any, error)
	QuotedForm(env environment.Env) (any, error)
	Repr() string
}
