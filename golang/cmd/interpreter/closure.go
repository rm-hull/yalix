package interpreter

import (
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

type closure struct {
	Primitive[any]
	env    environment.Env[any]
	lambda lambda
}

func Closure(env environment.Env[any], lambda lambda) closure {
	return closure{
		env:    env,
		lambda: lambda,
	}
}

func (c closure) Eval(env environment.Env[any]) (any, error) {
	return c, nil
}

func (c closure) Apply(env environment.Env[any], caller Caller) (any, error) {
	if !c.lambda.HasSufficientArity(caller.params) {
		return nil, errors.Errorf("call to '%s' applied with insufficient arity: %d args expected, %d supplied",
			// # FIXME: probably ought rely on __repr__ of symbol here....
			caller.funexp,
			c.lambda.Arity(),
			len(caller.params))
	}

	if !c.lambda.isVariadic && c.lambda.formals.Len() != len(caller.params) {
		return nil, errors.Errorf("call to '%s' applied with excessive arity: %d args expected, %d supplied",
			// # FIXME: probably ought rely on __repr__ of symbol here....
			caller.funexp,
			c.lambda.Arity(),
			len(caller.params))
	}

	extendedEnv, err := bind(c.env, c.lambda.formals, caller.params, env)
	if err != nil {
		return nil, err
	}
	return c.lambda.body.Eval(extendedEnv)
}

func bind(envToExtend environment.Env[any], formals list, params []Primitive[any], callerEnv environment.Env[any]) (environment.Env[any], error) {
	for i, bindVariable := range formals.items {
		if bindVariable == VARIADIC_MARKER { // variadic arg indicator
			
			// TODO: Realize
			// value, err := List(params[i:]...).Eval(callerEnv)
			// if err != nil {
			// 	return environment.Env[any]{}, errors.Errorf("unable to eval '%s'", params[i:])
			// }
			// envToExtend = envToExtend.Extend(formals.items[i+1].Repr(), value)
			
			// Use the next formal as the _actual_ bind variable,
			// evaluate the remaining arguments into a list (NOTE offset from i)
			// and dont process any more arguments
			envToExtend = envToExtend.Extend(formals.items[i+1].Repr(), List(params[i:]...))
			break

		} else {
			value, err := params[i].Eval(callerEnv)
			if err != nil {
				return environment.Env[any]{}, errors.Errorf("unable to eval '%s'", params[i])
			}
			envToExtend = envToExtend.Extend(bindVariable.Repr(), value)
		}
	}
	envToExtend.IncreaseStackDepth()
	return envToExtend, nil
}
