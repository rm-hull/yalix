package interpreter

import (
	"testing"
	"yalix/cmd/environment"

	"github.com/pkg/errors"
	"github.com/stretchr/testify/require"
)

func variadicAdd(args ...any) (any, error) {
	var total = 0
	list, ok := args[0].([]any)
	if !ok {
		return nil, errors.Errorf("cannot convert '%s' to []any", args[0])
	}
	for _, value := range list {
		intValue, ok := value.(int)
		if !ok {
			return nil, errors.Errorf("cannot convert '%s' to int", value)
		}
		total += intValue
	}
	return total, nil
}

func Test_Lambda(t *testing.T) {
	env := environment.MakeEnv[any]()
	closure, err := MakeGoFuncHandler(variadicAdd, 1, true).Eval(env)
	if err != nil {
		t.Error(err)
	}
	env.SetGlobal("+", closure)
	env.SetGlobal("*debug*", true)

	t.Run("Variadic apply", func(t *testing.T) {
		result, err := List(Symbol("+"), Atom(15), Atom(11), Atom(9), Atom(3)).Eval(env)
		require.Nil(t, err)
		require.Equal(t, 38, result)
	})
}
