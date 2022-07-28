package operator

import "github.com/pkg/errors"

func Eq(args ...any) (any, error) {
	list, err := parseList(args[0])
	if err != nil {
		return nil, err
	}
	switch len(list) {
	case 0:
		return nil, errors.Errorf("equality check applied with insufficient arity: 1+ args expected, %d supplied", len(list))

	case 1:
		return true, nil

	default:
		var prev any = list[0]
		for _, value := range list[1:] {
			if prev != value {
				return false, nil
			}
			prev = value
		}
		return true, nil
	}
}
