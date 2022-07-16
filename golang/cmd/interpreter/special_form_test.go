package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/stretchr/testify/require"
)

func Test_SpecialForm(t *testing.T) {
	env := environment.MakeEnv[any]()

	sf := SpecialForm("quote")

	t.Run("Eval", func(t *testing.T) {
		result, err := sf.Eval(env)
		require.Nil(t, err)
		require.Equal(t, sf.name, result.(specialForm).name)
		require.NotNil(t, result.(specialForm).impl)
	})

	t.Run("Apply", func(t *testing.T) {
		symbol := Symbol("test")
		caller := MakeCaller[any](Symbol("unused"), symbol)
		result, err := sf.Apply(env, caller)
		require.Nil(t, err)
		require.Equal(t, symbol, result)
	})
}
