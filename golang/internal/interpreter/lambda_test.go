package interpreter

import (
	"testing"
	"yalix/internal/environment"
	"yalix/internal/operator"

	"github.com/stretchr/testify/require"
)

func Test_Lambda(t *testing.T) {
	env := environment.MakeEnv[any]()
	closure, err := MakeGoFuncHandler(operator.Add, 1, true).Eval(env)
	if err != nil {
		t.Error(err)
	}
	env.SetGlobal("+", closure)
	env.SetGlobal("*debug*", true)

	t.Run("Variadic apply", func(t *testing.T) {
		result, err := List(Symbol("+"), Atom(15), Atom(11), Atom(9), Atom(3)).Eval(env)
		require.Nil(t, err)
		require.Equal(t, 38, result)
	})

	t.Run("Wrong type", func(t *testing.T) {
		result, err := List(Symbol("+"), Atom(15), Atom("tomato"), Atom(9), Atom(3)).Eval(env)
		require.EqualError(t, err, "cannot convert 'tomato' (string) to int")
		require.Nil(t, result)
	})
}
