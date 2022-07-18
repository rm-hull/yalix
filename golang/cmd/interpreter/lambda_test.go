package interpreter

import (
	"testing"
	"yalix/cmd/environment"
)

func Test_Lambda(t *testing.T) {
	env := environment.MakeEnv[any]()
	closure, err := MakeGoFuncHandler(add, 1, true).Eval(env)
	if err != nil {
		t.Error(err)
	}
	env.SetGlobal("+", closure)
	env.SetGlobal("*debug*", true)

	t.Run("Apply", func(t *testing.T) {
		// FIXME: in progress
		// result, err := List(Symbol("+"), Atom(15), Atom(11), Atom(9), Atom(3)).Eval(env)
		// require.Nil(t, err)
		// require.Equal(t, 38, result)
	})
}
