package interpreter

import (
	"testing"

	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Let(t *testing.T) {
	env := environment.MakeEnv()
	closure, err := MakeGoFuncHandler(func(args ...any) (any, error) { return args[0], nil }, 1, true).Eval(env)
	if err != nil {
		t.Error(err)
	}
	env.SetGlobal("list", closure)

	t.Run("Let", func(t *testing.T) {
		result, err := Let(List(Symbol("f"), Atom("Hello")),
			List(Symbol("list"), Symbol("f"), Symbol("f"))).Eval(env)
		require.Nil(t, err)
		require.Equal(t, []any{"Hello", "Hello"}, result)
	})

	t.Run("Invalid binding", func(t *testing.T) {
		result, err := Let(List(Symbol("f"), Atom("Hello"), Atom(3)),
			List(Symbol("list"), Symbol("f"), Symbol("f"))).Eval(env)
		require.EqualError(t, err, "let binding applied with wrong arity: 2 args expected, 3 supplied")
		require.Nil(t, result)
	})

	t.Run("Invalid binding form type", func(t *testing.T) {
		result, err := Let(List(Atom("Hello"), Atom(3)),
			List(Symbol("list"), Symbol("f"), Symbol("f"))).Eval(env)
		require.EqualError(t, err, "let binding form applied with invalid type: cannot convert 'Hello' (interpreter.atom) to interpreter.symbol")
		require.Nil(t, result)
	})
}
