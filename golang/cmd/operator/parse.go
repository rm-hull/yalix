package operator

import (
	"github.com/pkg/errors"
)

func parseNumber[T int | int32 | int64 | float32 | float64](value any) (T, error) {
	tValue, ok := value.(T)
	if !ok {
		return 0, errors.Errorf("cannot convert '%s' to number", value)
	}
	return tValue, nil
}

func parseList(value any) ([]any, error) {
	list, ok := value.([]any)
	if !ok {
		return nil, errors.Errorf("cannot convert '%s' to []any", value)
	}
	return list, nil
}
