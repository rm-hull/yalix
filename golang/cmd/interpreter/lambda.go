package interpreter

import "yalix/cmd/environment"

type lambda struct {
	Primitive[any]
	formals list
	body    body
}

// A recursive n-argument anonymous function
func Lambda(formals list, body ...Primitive[any]) lambda {
	return lambda{
		formals: formals,
		body:    Body(body...),
	}
}

func (l lambda) Arity() int {
	return l.formals.Len()
}

func (l lambda) HasSufficientArity(args []Primitive[any]) bool {
	return l.Arity() == len(args)
}

func (l lambda) Eval(env environment.Env[any]) (any, error) {
	return Closure(env, l), nil
}
