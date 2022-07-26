package interpreter

import (
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

type let struct {
	BuiltIn[any]
	binding list
	body    body
}

// A local binding
func Let(binding list, body ...Primitive[any]) let {
	return let{
		binding: binding,
		body:    Body(body...),
	}
}

func (l let) Eval(env environment.Env[any]) (any, error) {
	if l.binding.Len() != 2 {
		return nil, errors.Errorf("let binding applied with wrong arity: 2 args expected, %d supplied", l.binding.Len())
	}

	bindingForm, ok := l.binding.items[0].(symbol)
	if !ok {
		return nil, errors.New("let binding form applied with invalid type: expected symbol")
	}
	value, err := l.binding.items[1].Eval(env)
	if err != nil {
		return nil, err
	}

	extendedEnv := env.Extend(bindingForm.name, value)
	extendedEnv.IncreaseStackDepth()
	return l.body.Eval(extendedEnv)
}
