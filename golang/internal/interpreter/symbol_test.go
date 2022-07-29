package interpreter

import (
	"testing"

	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Symbol(t *testing.T) {
	env := environment.MakeEnv().Extend("fred", 45)
	symbol := Symbol("fred")
	result, err := symbol.Eval(env)
	require.Nil(t, err)
	require.Equal(t, 45, result)
	require.Equal(t, "fred", symbol.Repr())
}
