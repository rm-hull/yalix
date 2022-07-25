package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/stretchr/testify/require"
)

func Test_If(t *testing.T) {
	env := environment.MakeEnv[any]()

	t.Run("Truthy", func(t *testing.T) {
		result, err := If(Atom(true), Atom("yes"), Atom("No")).Eval(env)
		require.Nil(t, err)
		require.Equal(t, "yes", result)
	})

	t.Run("Falsy", func(t *testing.T) {
		result, err := If(Atom(false), Atom("yes"), NIL).Eval(env)
		require.Nil(t, err)
		require.Equal(t, nil, result)
	})

}
