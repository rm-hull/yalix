package interpreter

import "yalix/internal/environment"

type unbound struct {
	BuiltIn[any]
}

func Unbound() unbound {
	return unbound{}
}

func (u unbound) Eval(env environment.Env[any]) (any, error) {
	return u, nil
}
