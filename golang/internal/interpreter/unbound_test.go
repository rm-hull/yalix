package interpreter

import (
	"testing"

	"yalix/internal/environment"

	"github.com/stretchr/testify/require"
)

func Test_Unbound(t *testing.T) {
	env := environment.MakeEnv()

	t.Run("Eval", func(t *testing.T) {
		_, err := List(Unbound()).Eval(env)
		require.EqualError(t, err, "cannot invoke with: <unbound>")
	})
}
