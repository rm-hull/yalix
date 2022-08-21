package interpreter

import (
	"testing"

	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Atom(t *testing.T) {
	env := environment.MakeEnv()
	atom := Atom(56)
	result, err := atom.Eval(env)
	require.Nil(t, err)
	require.Equal(t, 56, result)
}