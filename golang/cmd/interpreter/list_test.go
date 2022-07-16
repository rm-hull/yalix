package interpreter_test

// import (
// 	"testing"

// 	"yalix/cmd/environment"

// 	"github.com/pkg/errors"
// 	"github.com/stretchr/testify/require"
// )

// func add(args ...any) (any, error) {
// 	var total = 0
// 	for _, value := range args {
// 		intValue, ok := value.(int)
// 		if !ok {
// 			return nil, errors.Errorf("cannot convert value '%s' to int", value)
// 		}
// 		total += intValue
// 	}
// 	return total, nil
// }

// func Test_List(t *testing.T) {
// 	env := environment.MakeEnv[any]()
// 	env.SetGlobal("+", InterOp(add))

// 	result, err := List(Symbol("+"), Atom(15), Atom(12)).Eval(env)
// 	require.Nil(t, err)
// 	require.Equal(t, 5, result)
// }
