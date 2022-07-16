package interpreter

import "yalix/cmd/environment"

// class InterOp(Primitive):
//     """ Helper class for wrapping Python functions """

//     def __init__(self, func, *args):
//         self.func = func
//         self.args = args

//     def eval(self, env):
//         values = [a.eval(env) for a in self.args]
//         try:
//             return self.func(*values)
//         except TypeError as ex:
//             raise EvaluationError(self, str(ex))

type interOp struct {
	fn   func(args ...any) (any, error)
	args []Primitive[any]
}

func InterOp(fn func(args ...any) (any, error), args ...Primitive[any]) interOp {
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
