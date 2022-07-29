package util

import (
	"reflect"

	"github.com/pkg/errors"
)

func CastAs[T any](value any) (T, error) {
	tValue, ok := value.(T)
	if !ok {
		return tValue, errors.Errorf("cannot convert '%v' (%s) to %s", value, reflect.TypeOf(value), reflect.TypeOf(tValue))
	}
	return tValue, nil
}
