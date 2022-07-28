package operator

import "yalix/cmd/util"

func Add(args ...any) (any, error) {
	var total = 0
	list, err := util.Parse[[]any](args[0])
	if err != nil {
		return nil, err
	}
	for _, value := range list {
		intValue, err := util.Parse[int](value)
		if err != nil {
			return nil, err
		}
		total += intValue
	}
	return total, nil
}

func Sub(args ...any) (any, error) {
	list, err := util.Parse[[]any](args[0])
	if err != nil {
		return nil, err
	}

	switch len(list) {
	case 0:
		return 0, nil

	case 1:
		intValue, err := util.Parse[int](list[0])
		if err != nil {
			return nil, err
		}
		return -intValue, nil

	default:
		total, err := util.Parse[int](list[0])
		if err != nil {
			return nil, err
		}

		for _, value := range list[1:] {
			intValue, err := util.Parse[int](value)
			if err != nil {
				return nil, err
			}
			total -= intValue
		}
		return total, nil
	}
}

func Mult(args ...any) (any, error) {
	list, err := util.Parse[[]any](args[0])
	if err != nil {
		return nil, err
	}

	var total = 1
	for _, value := range list {
		intValue, err := util.Parse[int](value)
		if err != nil {
			return nil, err
		}
		total *= intValue
	}
	return total, nil
}
