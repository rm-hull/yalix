package interpreter

import "yalix/internal/environment"

type unbound struct {
	BuiltIn
}

func Unbound() unbound {
	return unbound{}
}

func (u unbound) Eval(env environment.Env) (any, error) {
	return u, nil
}
