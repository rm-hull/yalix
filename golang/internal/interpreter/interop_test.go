package interpreter

import (
	"testing"

	"yalix/internal/environment"
	"yalix/internal/interop/operator"

	"github.com/stretchr/testify/require"
)

func tmp_add(args ...any) (any, error) {
	return operator.Add(args)
}

func Test_InterOp(t *testing.T) {
	env := environment.MakeEnv()

	result, err := InterOp(tmp_add, Atom(12), Atom(13)).Eval(env)
	require.Nil(t, err)
	require.Equal(t, 25, result)
}
