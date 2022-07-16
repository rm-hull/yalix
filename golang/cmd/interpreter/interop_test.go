package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/pkg/errors"
	"github.com/stretchr/testify/require"
)

func tmp_add(args ...any) (any, error) {
	var total = 0
	for _, value := range args {
		intValue, ok := value.(int)
		if !ok {
			return nil, errors.Errorf("cannot convert value '%s' to int", value)
		}
		total += intValue
	}
	return total, nil
}

func Test_InterOp(t *testing.T) {
	env := environment.MakeEnv[any]()

	result, err := InterOp(tmp_add, Atom(12), Atom(13)).Eval(env)
	require.Nil(t, err)
	require.Equal(t, 25, result)
}
