package operator

import (
	"reflect"
	"yalix/internal/types"
	"yalix/internal/util"

	"github.com/pkg/errors"
)

type comparatorFunc[T any] func(a, b T) bool

func compare[T any](name string, comparator comparatorFunc[T]) types.InterOpFunc {
	return func(args ...any) (any, error) {
		list, err := util.CastAs[[]any](args[0])
		if err != nil {
			return nil, err
		}
		switch len(list) {
		case 0:
			return nil, errors.Errorf("comparison check (%s) applied with insufficient arity: 1+ args expected, %d supplied", name, len(list))

		case 1:
			return true, nil

		default:
			prev, err := util.CastAs[T](list[0])
			if err != nil {
				return nil, err
			}
			for _, value := range list[1:] {
				curr, err := util.CastAs[T](value)
				if err != nil {
					return nil, err
				}
				if !comparator(prev, curr) {
					return false, nil
				}
			}
			return true, nil
		}
	}
}

func GreaterThan[T string | int](args ...any) (any, error) {
	return compare(">", func(a, b T) bool { return a > b })(args...)
}

func GreaterThanOrEqual[T string | int](args ...any) (any, error) {
	return compare(">=", func(a, b T) bool { return a >= b })(args...)
}

func LessThan[T string | int](args ...any) (any, error) {
	return compare("<", func(a, b T) bool { return a < b })(args...)
}

func LessThanOrEqual[T string | int](args ...any) (any, error) {
	return compare("<=", func(a, b T) bool { return a <= b })(args...)
}

func Equal(args ...any) (any, error) {
	return compare("=", func(a, b any) bool { return reflect.DeepEqual(a, b) })(args...)
}

func NotEqual(args ...any) (any, error) {
	result, err := compare("!=", func(a, b any) bool { return reflect.DeepEqual(a, b) })(args...)
	if err != nil {
		return nil, err
	}
	boolResult, err := util.CastAs[bool](result)

	if err != nil {
		return nil, err
	}
	return !boolResult, nil
}
