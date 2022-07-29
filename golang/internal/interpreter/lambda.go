package interpreter

import (
	"yalix/internal/environment"

	"github.com/pkg/errors"
)

var VARIADIC_MARKER = Symbol(".")

type lambda struct {
	Primitive
	formals    list
	body       body
	isVariadic bool
}

// A recursive n-argument anonymous function
func Lambda(formals list, body ...Primitive) lambda {
	return lambda{
		formals:    formals,
		body:       Body(body...),
		isVariadic: formals.Includes(VARIADIC_MARKER),
	}
}

func (l lambda) Arity() int {
	return l.formals.Len()
}

func (l lambda) HasSufficientArity(args []Primitive) bool {
	if l.isVariadic {
		return len(args) >= l.formals.Index(VARIADIC_MARKER)
	}
	return len(args) == l.Arity()
}

func (l lambda) Eval(env environment.Env) (any, error) {
	if l.isVariadic {
		if l.formals.Count(VARIADIC_MARKER) > 1 {
			return nil, errors.Errorf("invalid variadic argument spec: %s", l.formals)
		}
		if l.formals.Index(VARIADIC_MARKER) != l.formals.Len()-2 {
			return nil, errors.Errorf("only one variadic argument is allowed: %s", l.formals)
		}
	}
	return Closure(env, l), nil
}

// if len(self.formals) != len(set(self.formals)):
// 		raise EvaluationError(
// 				self, 'Formals are not distinct: {0}', self.formals)

// return Closure(env, self)
