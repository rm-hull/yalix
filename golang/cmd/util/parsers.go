package util

import (
	"reflect"

	"github.com/pkg/errors"
)

func Parse[T int | int32 | int64 | float32 | float64 | bool | []any](value any) (T, error) {
	tValue, ok := value.(T)
	if !ok {
		return tValue, errors.Errorf("cannot convert '%s' (%s) to %s", value, reflect.TypeOf(value), reflect.TypeOf(tValue))
	}
	return tValue, nil
}
