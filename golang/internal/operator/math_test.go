package operator

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_Add(t *testing.T) {

	t.Run("No args", func(t *testing.T) {
		result, err := Add([]any{})
		require.Nil(t, err)
		require.Equal(t, 0, result)
	})

	t.Run("Single args", func(t *testing.T) {
		result, err := Add([]any{4})
		require.Nil(t, err)
		require.Equal(t, 4, result)
	})

	t.Run("Mulitple args", func(t *testing.T) {
		result, err := Add([]any{1, 2, 3, 4})
		require.Nil(t, err)
		require.Equal(t, 10, result)
	})

	t.Run("Not a list", func(t *testing.T) {
		result, err := Add(5, 6)
		require.EqualError(t, err, "cannot convert '5' (int) to []interface {}")
		require.Nil(t, result)
	})

	t.Run("Invalid element type", func(t *testing.T) {
		result, err := Add([]any{1, 2, "potato", 4})
		require.EqualError(t, err, "cannot convert 'potato' (string) to int")
		require.Nil(t, result)
	})
}

func Test_Sub(t *testing.T) {

	t.Run("No args", func(t *testing.T) {
		result, err := Sub([]any{})
		require.Nil(t, err)
		require.Equal(t, 0, result)
	})

	t.Run("Single arg", func(t *testing.T) {
		result, err := Sub([]any{4})
		require.Nil(t, err)
		require.Equal(t, -4, result)
	})

	t.Run("Single arg invalid element type", func(t *testing.T) {
		result, err := Sub([]any{"potato"})
		require.EqualError(t, err, "cannot convert 'potato' (string) to int")
		require.Nil(t, result)
	})

	t.Run("Mulitple args", func(t *testing.T) {
		result, err := Sub([]any{10, 5, 2})
		require.Nil(t, err)
		require.Equal(t, 3, result)
	})

	t.Run("Multiple args invalid first element type", func(t *testing.T) {
		result, err := Sub([]any{"cucumber", 1, 2, "potato", 4})
		require.EqualError(t, err, "cannot convert 'cucumber' (string) to int")
		require.Nil(t, result)
	})

	t.Run("Multiple args invalid element type", func(t *testing.T) {
		result, err := Sub([]any{1, 2, "potato", 4})
		require.EqualError(t, err, "cannot convert 'potato' (string) to int")
		require.Nil(t, result)
	})

	t.Run("Not a list", func(t *testing.T) {
		result, err := Sub(5, 6)
		require.EqualError(t, err, "cannot convert '5' (int) to []interface {}")
		require.Nil(t, result)
	})
}

func Test_Mult(t *testing.T) {

	t.Run("No args", func(t *testing.T) {
		result, err := Mult([]any{})
		require.Nil(t, err)
		require.Equal(t, 1, result)
	})

	t.Run("Single args", func(t *testing.T) {
		result, err := Mult([]any{4})
		require.Nil(t, err)
		require.Equal(t, 4, result)
	})

	t.Run("Mulitple args", func(t *testing.T) {
		result, err := Mult([]any{1, 2, 3, 4})
		require.Nil(t, err)
		require.Equal(t, 24, result)
	})

	t.Run("Not a list", func(t *testing.T) {
		result, err := Mult(5, 6)
		require.EqualError(t, err, "cannot convert '5' (int) to []interface {}")
		require.Nil(t, result)
	})

	t.Run("Invalid element type", func(t *testing.T) {
		result, err := Mult([]any{1, 2, "potato", 4})
		require.EqualError(t, err, "cannot convert 'potato' (string) to int")
		require.Nil(t, result)
	})
}
