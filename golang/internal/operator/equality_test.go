package operator

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_Eq(t *testing.T) {

	t.Run("No args", func(t *testing.T) {
		result, err := Eq([]any{})
		require.EqualError(t, err, "equality check applied with insufficient arity: 1+ args expected, 0 supplied")
		require.Nil(t, result)
	})

	t.Run("Single args", func(t *testing.T) {
		result, err := Eq([]any{4})
		require.Nil(t, err)
		require.Equal(t, true, result)
	})

	t.Run("Mulitple args, not equal", func(t *testing.T) {
		result, err := Eq([]any{1, 2, 3, 4})
		require.Nil(t, err)
		require.Equal(t, false, result)
	})

	t.Run("Mulitple args, nearly all equal", func(t *testing.T) {
		result, err := Eq([]any{7, 7, 7, 3, 7})
		require.Nil(t, err)
		require.Equal(t, false, result)
	})

	t.Run("Mulitple args, equal strings", func(t *testing.T) {
		result, err := Eq([]any{"yes", "yes", "yes"})
		require.Nil(t, err)
		require.Equal(t, true, result)
	})

	t.Run("Mulitple args, equal arrays", func(t *testing.T) {
		result, err := Eq([]any{[]int{1, 2, 3}, []int{1, 2, 3}})
		require.Nil(t, err)
		require.Equal(t, true, result)
	})

	t.Run("Not a list", func(t *testing.T) {
		result, err := Eq(5, 6)
		require.EqualError(t, err, "cannot convert '5' (int) to []interface {}")
		require.Nil(t, result)
	})

	t.Run("Different element types", func(t *testing.T) {
		result, err := Eq([]any{1, 2, "potato", 4})
		require.Nil(t, err)
		require.Equal(t, false, result)
	})
}
