package internal

import (
	"testing"
	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Global(t *testing.T) {

	env := environment.MakeEnv()

	BootstrapSpecialForms(&env)
	err := BootstrapNativeFunctions(&env)
	require.Nil(t, err)
	// err = BootstrapLispFunctions(&env, "/Users/richardhull/dev/yalix/core/num.ylx")
	// require.Nil(t, err)

	result, err := eval(&env, `
		; Factorial test
		; --------------

		(define (zero? n)
			(= n 0))

		(define factorial
			(lambda (x)
				(if (zero? x)
					1
					(* x (factorial (- x 1))))))

		(factorial 10)`)
	require.Nil(t, err)
	require.Equal(t, 3628800, result)
}
