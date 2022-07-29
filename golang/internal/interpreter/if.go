package interpreter

import (
	"yalix/internal/environment"
	"yalix/internal/util"
)

type _if struct {
	BuiltIn
	testExpr Primitive
	thenExpr Primitive
	elseExpr Primitive
}

func (i _if) Eval(env environment.Env) (any, error) {
	test, err := i.testExpr.Eval(env)
	if err != nil {
		return nil, err
	}

	result, err := util.CastAs[bool](test)
	if err != nil {
		return nil, err
	}

	if result {
		return i.thenExpr.Eval(env)
	} else {
		return i.elseExpr.Eval(env)
	}
}

func If(testExpr, thenExpr, elseExpr Primitive) _if {
	return _if{
		testExpr: testExpr,
		thenExpr: thenExpr,
		elseExpr: elseExpr,
	}
}
