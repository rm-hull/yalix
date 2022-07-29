package interpreter

import (
	"yalix/internal/environment"
)

type body struct {
	BuiltIn
	exprs []Primitive
}

func Body(exprs ...Primitive) body {
	return body{
		exprs: exprs,
	}
}

func (b body) Eval(env environment.Env) (any, error) {
	var result any
	var err error
	for _, expr := range b.exprs {
		result, err = expr.Eval(env)
		if err != nil {
			return nil, err
		}
	}
	return result, nil
}
