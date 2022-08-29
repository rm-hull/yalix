package operator

import (
	"yalix/internal/util"

	"github.com/pkg/errors"
)

type tuple struct {
	car any
	cdr any
}

func Cons(args ...any) (any, error) {
	return tuple{car: args[0], cdr: args[1]}, nil
}

func Car(args ...any) (any, error) {
	if args[0] == nil {
		return nil, nil
	}

	consCell, err := util.CastAs[tuple](args[0])
	if err != nil {
		return nil, errors.Errorf("cannot call car on non-cons cell: '%+v'", args[0])
	}

	return consCell.car, nil
}

func Cdr(args ...any) (any, error) {
	if args[0] == nil {
		return nil, nil
	}

	consCell, err := util.CastAs[tuple](args[0])
	if err != nil {
		return nil, errors.Errorf("cannot call cdr on non-cons cell: '%+v'", args[0])
	}

	return consCell.cdr, nil
}
