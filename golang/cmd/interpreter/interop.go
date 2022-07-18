package interpreter

import (
	"yalix/cmd/environment"
)

type interOpFunc func(args ...any) (any, error)

type interOp struct {
	Primitive[any]
	fn   interOpFunc
	args []Primitive[any]
}

func InterOp(fn interOpFunc, args ...Primitive[any]) interOp {
	return interOp{
		fn:   fn,
		args: args,
	}
}

func (i interOp) Eval(env environment.Env[any]) (any, error) {
	var values = []any{}
	for _, arg := range i.args {
		value, err := arg.Eval(env)
		if err != nil {
			return nil, err
		}
		values = append(values, value)
	}
	return i.fn(values...)
}

func MakeGoFuncHandler(fn interOpFunc, arity uint, variadic bool) lambda {

	// if variadic && arity < 1 {
	// 	return lambda{}, errors.New("must be at least arity-1 when variadic == true")
	// }

	bindVariables := make([]Primitive[any], arity)
	for i := range bindVariables {
		bindVariables[i] = GenSym()
	}

	var formals = bindVariables
	if variadic {
		// # Insert the variadic marker at the last-but one position
		index := len(bindVariables) - 1
		formals = append(formals[:index+1], formals[index:]...)
		formals[index] = VARIADIC_MARKER
		// TODO: Realize
	}

	return Lambda(List(formals...), InterOp(fn, bindVariables...))
}
