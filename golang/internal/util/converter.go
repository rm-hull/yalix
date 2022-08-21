package util

import (
	"github.com/pkg/errors"
)

func CastAs[T any](value any) (T, error) {
	tValue, ok := value.(T)
	if !ok {
		return tValue, errors.Errorf("cannot convert '%v' (%T) to %T", value, value, tValue)
	}
	return tValue, nil
}
