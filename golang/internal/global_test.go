package internal

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_Global(t *testing.T) {

	env, err := CreateInitialEnv()
	require.Nil(t, err)

	result, err := eval(env, `
		; Factorial test
		; --------------
		(define factorial
			(lambda (x)
				(if (zero? x)
					1
					(* x (factorial (- x 1))))))

		(factorial 10)`)
	require.Nil(t, err)
	require.Equal(t, 3628800, result)
}
