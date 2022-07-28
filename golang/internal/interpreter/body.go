package interpreter

import (
	"yalix/internal/environment"
)

type body struct {
	BuiltIn[any]
	exprs []Primitive[any]
}

func Body(exprs ...Primitive[any]) body {
	return body{
		exprs: exprs,
	}
}

func (b body) Eval(env environment.Env[any]) (any, error) {
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
