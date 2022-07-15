package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/stretchr/testify/require"
)

func Test_Quote(t *testing.T) {
	env := environment.MakeEnv[any]()

	t.Run("Atom", func(t *testing.T) {
		q, err := Quote(Atom[any](5)).Eval(env)
		require.Nil(t, err)
		require.Equal(t, 5, q)
	})

	t.Run("Symbol", func(t *testing.T) {
		q, err := Quote(Symbol("toil")).Eval(env)
		require.Nil(t, err)
		require.IsType(t, symbol{}, q)
		require.Equal(t, "toil", q.(symbol).name)
	})
}
