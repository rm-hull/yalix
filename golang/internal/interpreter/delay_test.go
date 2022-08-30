package interpreter

import (
	"testing"
	"yalix/internal/environment"
	"yalix/internal/util"

	"github.com/stretchr/testify/require"
)

func TestDelay(t *testing.T) {
	env := environment.MakeEnv()

	t.Run("Promise apply", func(t *testing.T) {
		result, err := List(SpecialForm("delay"), Atom(5)).Eval(env)
		require.Nil(t, err)

		promise, err := util.CastAs[*promise](result)
		require.Nil(t, err)
		require.False(t, promise.realized)

		result2, err := promise.Apply(env, MakeCaller(Symbol("n/a")))
		require.Nil(t, err)
		require.True(t, promise.realized)
		require.Equal(t, 5, result2)

		result3, err := promise.Apply(env, MakeCaller(Symbol("n/a")))
		require.Nil(t, err)
		require.True(t, promise.realized)
		require.Equal(t, 5, result3)
	})

	t.Run("Eval", func(t *testing.T) {
		result, err := List(List(SpecialForm("delay"), Atom(5))).Eval(env)
		require.Nil(t, err)
		require.Equal(t, 5, result)
	})
}
