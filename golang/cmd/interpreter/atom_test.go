package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/stretchr/testify/require"
)

func Test_Atom(t *testing.T) {
	env := environment.MakeEnv[any]()
	atom := Atom[any](56)
	result, err := atom.Eval(env)
	require.Equal(t, 56, result)
	require.Nil(t, err)
}
