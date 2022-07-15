package environment

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_LocalStack(t *testing.T) {

	t.Run("Extend", func(t *testing.T) {
		env := MakeEnv[any]()
		env.SetGlobal("a", 1)
		newEnv := env.Extend("x", 2)

		result, err := env.Get("a")
		require.Equal(t, 1, result)
		require.Nil(t, err)

		result, err = env.Get("x")
		require.Nil(t, result)
		require.EqualError(t, err, "'x' is unbound in environment")

		result, err = newEnv.Get("a")
		require.Equal(t, 1, result)
		require.Nil(t, err)

		result, err = newEnv.Get("x")
		require.Equal(t, 2, result)
		require.Nil(t, err)
	})

	t.Run("Shadowing", func(t *testing.T) {
		env := MakeEnv[any]()
		newEnvA := env.Extend("x", 2)
		newEnvB := newEnvA.Extend("x", 5)

		result, err := env.Get("x")
		require.Nil(t, result)
		require.EqualError(t, err, "'x' is unbound in environment")

		result, err = newEnvA.Get("x")
		require.Equal(t, 2, result)
		require.Nil(t, err)

		result, err = newEnvB.Get("x")
		require.Equal(t, 5, result)
		require.Nil(t, err)
	})

	t.Run("Freevars", func(t *testing.T) {
		var env = MakeEnv[any]()
		env = env.Extend("a", 3)
		env = env.Extend("b", 17)
		env = env.Extend("c", 6)
		for i := 0; i < 10; i++ {
			env = env.Extend("b", i)
		}
		env = env.Extend("b", 55)
		env = env.Extend("c", 12)

		result, err := env.Get("a")
		require.Equal(t, 3, result)
		require.Nil(t, err)

		result, err = env.Get("b")
		require.Equal(t, 55, result)
		require.Nil(t, err)

		result, err = env.Get("c")
		require.Equal(t, 12, result)
		require.Nil(t, err)

		require.Equal(t, 3, len(env.localStack))
	})

	t.Run("Non-existent SetLocal", func(t *testing.T) {
		env := MakeEnv[any]()

		result, err := env.Get("a")
		require.Nil(t, result)
		require.EqualError(t, err, "'a' is unbound in environment")

		err = env.SetLocal("a", 5)
		require.EqualError(t, err, "Assignment disallowed: 'a' is unbound in local environment")
	})

	t.Run("SetLocal doesnt bleed", func(t *testing.T) {
		env := MakeEnv[any]()
		env.SetGlobal("a", 12) // Global frame

		extendedEnv := env.Extend("a", 16) // Local shadowing

		result, err := env.Get("a")
		require.Equal(t, 12, result)
		require.Nil(t, err)

		result, err = extendedEnv.Get("a")
		require.Equal(t, 16, result)
		require.Nil(t, err)

		// Now update global 'a' in original env - check it doesnt bleed into extended
		env.SetGlobal("a", 50)

		result, err = env.Get("a")
		require.Equal(t, 50, result)
		require.Nil(t, err)

		result, err = extendedEnv.Get("a")
		require.Equal(t, 16, result)
		require.Nil(t, err)

		// Update 'a' in extended env, check no bleeding again
		err = extendedEnv.SetLocal("a", 46)
		require.Nil(t, err)

		result, err = env.Get("a")
		require.Equal(t, 50, result)
		require.Nil(t, err)

		result, err = extendedEnv.Get("a")
		require.Equal(t, 46, result)
		require.Nil(t, err)
	})
}

// def test_contains(self):
// env = Env()
// self.assertFalse('a' in env)
// extended_env = env.extend('a', 16)
// self.assertFalse('a' in env)
// self.assertTrue('a' in extended_env)
