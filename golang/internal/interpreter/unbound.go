package interpreter

import (
	"yalix/internal/environment"

	"github.com/pkg/errors"
)

type unbound struct {
	BuiltIn
}

func Unbound() unbound {
	return unbound{}
}

func (u unbound) Eval(env environment.Env) (any, error) {
	return u, nil
}

func (u unbound) Apply(env environment.Env, caller Caller) (any, error) {
	return nil, errors.Errorf("cannot invoke with: <unbound>")
}
