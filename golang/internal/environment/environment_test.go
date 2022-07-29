package environment

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_LocalStack(t *testing.T) {

	t.Run("Extend", func(t *testing.T) {
		env := MakeEnv()
		env.SetGlobal("a", 1)
		newEnv := env.Extend("x", 2)

		result, err := env.Get("a")
		require.Nil(t, err)
		require.Equal(t, 1, result)

		result, err = env.Get("x")
		require.EqualError(t, err, "'x' is unbound in environment")
		require.Nil(t, result)

		result, err = newEnv.Get("a")
		require.Nil(t, err)
		require.Equal(t, 1, result)

		result, err = newEnv.Get("x")
		require.Nil(t, err)
		require.Equal(t, 2, result)
	})

	t.Run("Shadowing", func(t *testing.T) {
		env := MakeEnv()
		newEnvA := env.Extend("x", 2)
		newEnvB := newEnvA.Extend("x", 5)

		result, err := env.Get("x")
		require.EqualError(t, err, "'x' is unbound in environment")
		require.Nil(t, result)

		result, err = newEnvA.Get("x")
		require.Nil(t, err)
		require.Equal(t, 2, result)

		result, err = newEnvB.Get("x")
		require.Nil(t, err)
		require.Equal(t, 5, result)
	})

	t.Run("Freevars", func(t *testing.T) {
		var env = MakeEnv()
		env = env.Extend("a", 3)
		env = env.Extend("b", 17)
		env = env.Extend("c", 6)
		for i := 0; i < 10; i++ {
			env = env.Extend("b", i)
		}
		env = env.Extend("b", 55)
		env = env.Extend("c", 12)

		result, err := env.Get("a")
		require.Nil(t, err)
		require.Equal(t, 3, result)

		result, err = env.Get("b")
		require.Nil(t, err)
		require.Equal(t, 55, result)

		result, err = env.Get("c")
		require.Nil(t, err)
		require.Equal(t, 12, result)

		require.Equal(t, 3, len(env.localStack))
	})

	t.Run("Non-existent SetLocal", func(t *testing.T) {
		env := MakeEnv()

		result, err := env.Get("a")
		require.EqualError(t, err, "'a' is unbound in environment")
		require.Nil(t, result)

		err = env.SetLocal("a", 5)
		require.EqualError(t, err, "assignment disallowed: 'a' is unbound in local environment")
	})

	t.Run("SetLocal doesnt bleed", func(t *testing.T) {
		env := MakeEnv()
		env.SetGlobal("a", 12) // Global frame

		extendedEnv := env.Extend("a", 16) // Local shadowing

		result, err := env.Get("a")
		require.Nil(t, err)
		require.Equal(t, 12, result)

		result, err = extendedEnv.Get("a")
		require.Nil(t, err)
		require.Equal(t, 16, result)

		// Now update global 'a' in original env - check it doesnt bleed into extended
		env.SetGlobal("a", 50)

		result, err = env.Get("a")
		require.Nil(t, err)
		require.Equal(t, 50, result)

		result, err = extendedEnv.Get("a")
		require.Nil(t, err)
		require.Equal(t, 16, result)

		// Update 'a' in extended env, check no bleeding again
		err = extendedEnv.SetLocal("a", 46)
		require.Nil(t, err)

		result, err = env.Get("a")
		require.Nil(t, err)
		require.Equal(t, 50, result)

		result, err = extendedEnv.Get("a")
		require.Nil(t, err)
		require.Equal(t, 46, result)
	})

	t.Run("Includes", func(t *testing.T) {
		env := MakeEnv()
		env.SetGlobal("a", 29)
		extendedEnv := env.Extend("b", 16)

		require.True(t, env.Includes("a"))
		require.False(t, env.Includes("b"))
		require.True(t, extendedEnv.Includes("b"))
		require.False(t, extendedEnv.Includes("c"))
	})
}
