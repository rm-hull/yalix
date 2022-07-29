package interpreter

import (
	"testing"
	"yalix/internal/environment"
	"yalix/internal/operator"

	"github.com/stretchr/testify/require"
)

func _fact_body(name string) Primitive {
	return If(List(Symbol("zero?"), Symbol("x")),
		Atom(1),
		List(Symbol("*"),
			Symbol("x"),
			List(Symbol(name),
				List(Symbol("-"),
					Symbol("x"),
					Atom(1)))))
}

func _makeExtendedEnv() (*environment.Env, error) {
	env := environment.MakeEnv()
	env.SetGlobal("*debug*", false)

	_, err := Define(Symbol("*"), MakeGoFuncHandler(operator.Mult, 1, true)).Eval(env)
	if err != nil {
		return nil, err
	}
	_, err = Define(Symbol("+"), MakeGoFuncHandler(operator.Add, 1, true)).Eval(env)
	if err != nil {
		return nil, err
	}
	_, err = Define(Symbol("-"), MakeGoFuncHandler(operator.Sub, 1, true)).Eval(env)
	if err != nil {
		return nil, err
	}
	_, err = Define(Symbol("="), MakeGoFuncHandler(operator.Eq, 1, true)).Eval(env)
	if err != nil {
		return nil, err
	}
	_, err = Define(Symbol("zero?"), Lambda(List(Symbol("n")), List(
		Symbol("="), Symbol("n"), Atom(0)))).Eval(env)
	if err != nil {
		return nil, err
	}

	return &env, nil
}

func Test_Define(t *testing.T) {
	env := environment.MakeEnv()

	t.Run("Too many args", func(t *testing.T) {
		result, err := Define(Symbol("err"), Atom("atom1"), Atom(3)).Eval(env)
		require.EqualError(t, err, "too many arguments supplied to define")
		require.Nil(t, result)
	})

	t.Run("Too few args", func(t *testing.T) {
		result, err := Define().Eval(env)
		require.EqualError(t, err, "too few arguments supplied to define")
		require.Nil(t, result)
	})

	t.Run("Unbound", func(t *testing.T) {
		result, err := Define(Symbol("unbound")).Eval(env)
		require.Nil(t, err)
		require.Equal(t, Symbol("unbound"), result)

		result, err = Symbol("unbound").Eval(env)
		require.Nil(t, err)
		require.Equal(t, Unbound(), result)
	})

	t.Run("Constant", func(t *testing.T) {
		result, err := Define(Symbol("five"), Atom(5)).Eval(env)
		require.Nil(t, err)
		require.Equal(t, Symbol("five"), result)

		result, err = Symbol("five").Eval(env)
		require.Nil(t, err)
		require.Equal(t, 5, result)
	})

	t.Run("Function definition", func(t *testing.T) {
		// Equivalent to:
		//    (define factorial
		//      (lambda (x)
		//        (if (zero? x)
		//          1
		//          (* x (factorial (- x 1))))))

		extendedEnv, err := _makeExtendedEnv()
		if err != nil {
			t.Fatal(err)
		}

		// Two variants - define/lambda vs. syntactic sugar version
		_, err = Define(Symbol("factorial1"), Lambda(List(Symbol("x")), _fact_body("factorial1"))).Eval(*extendedEnv)
		require.Nil(t, err)

		_, err = Define(List(Symbol("factorial2"), Symbol("x")), _fact_body("factorial2")).Eval(*extendedEnv)
		require.Nil(t, err)

		// (factorial 10)
		result1, err := List(Symbol("factorial1"), Atom(10)).Eval(*extendedEnv)
		require.Nil(t, err)
		require.Equal(t, 3628800, result1)

		result2, err := List(Symbol("factorial2"), Atom(10)).Eval(*extendedEnv)
		require.Nil(t, err)
		require.Equal(t, 3628800, result2)
	})
}
