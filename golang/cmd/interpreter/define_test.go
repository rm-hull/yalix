package interpreter

import (
	"testing"
	"yalix/cmd/environment"

	"github.com/stretchr/testify/require"
)

// def test_function_defn(self):
// # Equivalent to:
// #   (define factorial
// #     (lambda (x)
// #       (if (zero? x)
// #         1
// #         (* x (factorial (- x 1))))))
// #
// env = make_env()

// def body(name):
// 		return If(List(Symbol('zero?'), Symbol('x')),
// 							Atom(1),
// 							List(Symbol('*'),
// 									 Symbol('x'),
// 									 List(Symbol(name),
// 												List(Symbol('-'),
// 														 Symbol('x'),
// 														 Atom(1)))))

// # Two variants - define/lambda vs. syntactic sugar version
// Define(Symbol('factorial1'), Lambda(
// 		List(Symbol('x')), body('factorial1'))).eval(env)
// Define(List(Symbol('factorial2'), Symbol('x')),
// 			 body('factorial2')).eval(env)

// # (factorial 10)
// value1 = List(Symbol('factorial1'), Atom(10)).eval(env)
// self.assertEquals(3628800, value1)

// value2 = List(Symbol('factorial2'), Atom(10)).eval(env)
// self.assertEquals(3628800, value2)

func Test_Define(t *testing.T) {
	env := environment.MakeEnv[any]()

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
}
