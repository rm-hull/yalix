package interpreter

import (
	"testing"

	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Symbol(t *testing.T) {
	env := environment.MakeEnv().Extend("fred", 45)

	t.Run("Eval", func(t *testing.T) {
		symbol := Symbol("fred")
		result, err := symbol.Eval(env)
		require.Nil(t, err)
		require.Equal(t, 45, result)
		require.Equal(t, "fred", symbol.Repr())
	})

	t.Run("Quoted", func(t *testing.T) {
		symbol1 := Symbol("bob#")
		result1, err := SyntaxQuote(symbol1).Eval(env)
		require.Nil(t, err)

		symbol2 := Symbol("bob#")
		result2, err := SyntaxQuote(symbol2).Eval(env)
		require.Nil(t, err)
		require.NotEqual(t, result1, result2)
	})
}
