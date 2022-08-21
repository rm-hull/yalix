package operator

import "github.com/pkg/errors"

func IsNil(args ...any) (any, error) {
	switch len(args) {
	case 1:
		return args[0] == nil, nil
	default:
		return nil, errors.Errorf("nil check applied with incorrect arity: 1 arg expected, %d supplied", len(args))
	}
}
