package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/stretchr/testify/require"
)

func Test_Symbol(t *testing.T) {
	env := environment.MakeEnv[any]().Extend("fred", 45)
	symbol := Symbol("fred")
	result, err := symbol.Eval(env)
	require.Equal(t, 45, result)
	require.Nil(t, err)
	require.Equal(t, "fred", symbol.Repr())
}
