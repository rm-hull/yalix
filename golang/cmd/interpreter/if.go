package interpreter

import (
	"yalix/cmd/environment"
	"yalix/cmd/util"
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

	result, err := util.Parse[bool](test)
	if err != nil {
		return nil, err
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
