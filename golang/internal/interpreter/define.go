package interpreter

import (
	"errors"
	"yalix/internal/environment"
)

type define struct {
	BuiltIn
	args []Primitive
}

func Define(args ...Primitive) define {
	return define{args: args}
}

func (d define) name() symbol {
	first, ok := d.args[0].(list)
	if ok {
		return first.items[0].(symbol)
	}
	return d.args[0].(symbol)
}

func (d define) body() body {
	return Body(d.args[1:]...)
}

func (d define) Eval(env environment.Env) (any, error) {

	if len(d.args) == 0 {
		return nil, errors.New("too few arguments supplied to define")
	}

	var obj any
	var err error
	symbol := d.name()

	first, ok := d.args[0].(list)
	if ok {
		formals := first.items[1:]
		obj, err = Lambda(List(formals...), d.body()).Eval(env)

	} else {
		body := d.body()
		switch len(body.exprs) {
		case 0:
			{
				obj = Unbound()
				break
			}
		case 1:
			{
				obj, err = body.exprs[0].Eval(env)
				break
			}
		default:
			err = errors.New("too many arguments supplied to define")
		}
	}

	if err != nil {
		return nil, err
	}

	env.SetGlobal(symbol.Repr(), obj)
	return symbol, nil
}
