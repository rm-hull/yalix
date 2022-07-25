// class If(BuiltIn):
//     """ If """

//     def __init__(self, test_expr, then_expr, else_expr=Atom(None)):
//         self.test_expr = test_expr
//         self.then_expr = then_expr
//         self.else_expr = else_expr

//     def eval(self, env):
//         if self.test_expr.eval(env):
//             return self.then_expr.eval(env)
//         else:
//             return self.else_expr.eval(env)
package interpreter

import (
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

type _if struct {
	BuiltIn[any]
	testExpr Primitive[any]
	thenExpr Primitive[any]
	elseExpr Primitive[any]
}

func (i _if) Eval(env environment.Env[any]) (any, error) {
	test, err := i.testExpr.Eval(env)
	if err != nil {
		return nil, err
	}

	result, ok := test.(bool)
	if !ok {
		return nil, errors.Errorf("Cannot convert '%s' to bool", test)
	}

	if result {
		return i.thenExpr.Eval(env)
	} else {
		return i.elseExpr.Eval(env)
	}
}

func If(testExpr, thenExpr, elseExpr Primitive[any]) _if {
	return _if{
		testExpr: testExpr,
		thenExpr: thenExpr,
		elseExpr: elseExpr,
	}
}
