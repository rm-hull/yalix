package interpreter

import (
	"testing"

	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Quote(t *testing.T) {
	env := environment.MakeEnv()

	t.Run("Atom", func(t *testing.T) {
		q, err := Quote(Atom(5)).Eval(env)
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
