package interpreter

import "yalix/cmd/environment"

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

func MakeHandler(fn interOpFunc, arity uint) lambda {

	bindVariables := make([]Primitive[any], arity)
	for i := range bindVariables {
		bindVariables[i] = GenSym()
	}
	formals := bindVariables

	return Lambda(List(formals...), InterOp(fn, bindVariables...))
}

// TODO: handle variadic interop
