package interpreter

import (
	"testing"

	"yalix/cmd/environment"

	"github.com/pkg/errors"
	"github.com/stretchr/testify/require"
)

func add(args ...any) (any, error) {
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

func Test_List(t *testing.T) {
	env := environment.MakeEnv[any]()
	closure, err := MakeGoFuncHandler(add, 2).Eval(env)
	if err != nil {
		t.Error(err)
	}
	env.SetGlobal("+", closure)
	env.SetGlobal("*debug*", true)

	t.Run("Apply", func(t *testing.T) {
		result, err := List(Symbol("+"), Atom(15), Atom(11)).Eval(env)
		require.Nil(t, err)
		require.Equal(t, 26, result)
	})

	t.Run("Call non-closure", func(t *testing.T) {
		extendedEnv := env.Extend("barf", Atom("barf"))
		result, err := List(Symbol("barf"), Atom(3)).Eval(extendedEnv)
		require.EqualError(t, err, "cannot invoke with: 'barf'", err)
		require.Nil(t, result)
	})
	
	t.Run("Wrong arity", func(t *testing.T) {
		// Porridge is too cold
		result, err := List(Symbol("+"), Atom(3)).Eval(env)
		require.EqualError(t, err, "call to '+' applied with insufficient arity: 2 args expected, 1 supplied", err)
		require.Nil(t, result)
		
		// # Porridge is too hot
		result, err = List(Symbol("+"), Atom(3), Atom(4), Atom(5)).Eval(env)
		require.EqualError(t, err, "call to '+' applied with insufficient arity: 2 args expected, 3 supplied", err)
		require.Nil(t, result)
	})
}
