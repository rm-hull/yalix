package interpreter

import "yalix/cmd/environment"

var VARIADIC_MARKER = Symbol(".")

type lambda struct {
	Primitive[any]
	formals    list
	body       body
	isVariadic bool
}

// A recursive n-argument anonymous function
func Lambda(formals list, body ...Primitive[any]) lambda {
	return lambda{
		formals:    formals,
		body:       Body(body...),
		isVariadic: formals.Includes(VARIADIC_MARKER),
	}
}

func (l lambda) Arity() int {
	return l.formals.Len()
}

func (l lambda) HasSufficientArity(args []Primitive[any]) bool {
	if l.isVariadic {
		return len(args) >= l.formals.Index(VARIADIC_MARKER)
	}
	return len(args) == l.Arity()
}

func (l lambda) Eval(env environment.Env[any]) (any, error) {
	return Closure(env, l), nil
}

// def eval(self, env):
// if self.is_variadic():
// 		if sum(1 for f in self.formals if f == Lambda.VARIADIC_MARKER) > 1:
// 				raise EvaluationError(
// 						self, 'Invalid variadic argument spec: {0}', self.formals)

// 		if self.formals.index(Lambda.VARIADIC_MARKER) != len(self.formals) - 2:
// 				raise EvaluationError(
// 						self, 'Only one variadic argument is allowed: {0}', self.formals)

// if len(self.formals) != len(set(self.formals)):
// 		raise EvaluationError(
// 				self, 'Formals are not distinct: {0}', self.formals)

// return Closure(env, self)
