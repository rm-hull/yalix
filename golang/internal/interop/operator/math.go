package operator

import (
	"yalix/internal/util"

	"github.com/pkg/errors"
)

func Add(args ...any) (any, error) {
	var total = 0
	list, err := util.CastAs[[]any](args[0])
	if err != nil {
		return nil, err
	}
	for _, value := range list {
		intValue, err := util.CastAs[int](value)
		if err != nil {
			return nil, err
		}
		total += intValue
	}
	return total, nil
}

func Sub(args ...any) (any, error) {
	list, err := util.CastAs[[]any](args[0])
	if err != nil {
		return nil, err
	}

	switch len(list) {
	case 0:
		return 0, nil

	case 1:
		intValue, err := util.CastAs[int](list[0])
		if err != nil {
			return nil, err
		}
		return -intValue, nil

	default:
		total, err := util.CastAs[int](list[0])
		if err != nil {
			return nil, err
		}

		for _, value := range list[1:] {
			intValue, err := util.CastAs[int](value)
			if err != nil {
				return nil, err
			}
			total -= intValue
		}
		return total, nil
	}
}

func Mult(args ...any) (any, error) {
	list, err := util.CastAs[[]any](args[0])
	if err != nil {
		return nil, err
	}

	var total = 1
	for _, value := range list {
		intValue, err := util.CastAs[int](value)
		if err != nil {
			return nil, err
		}
		total *= intValue
	}
	return total, nil
}

func Div(args ...any) (any, error) {
	list, err := util.CastAs[[]any](args[0])
	if err != nil {
		return nil, err
	}

	switch len(list) {
	case 0:
		return nil, errors.New("division by zero")

	case 1:
		intValue, err := util.CastAs[int](list[0])
		if err != nil {
			return nil, err
		}
		return 1 / intValue, nil

	default:
		total, err := util.CastAs[int](list[0])
		if err != nil {
			return nil, err
		}

		for _, value := range list[1:] {
			intValue, err := util.CastAs[int](value)
			if err != nil {
				return nil, err
			}
			total /= intValue
		}
		return total, nil
	}
}