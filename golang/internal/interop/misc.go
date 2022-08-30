package interop

import (
	"time"
	"yalix/internal/interpreter"
	"yalix/internal/util"
)

func EpochTime(args ...any) (any, error) {
	return time.Now().UnixMilli(), nil
}

func Symbol(args ...any) (any, error) {
	name, err := util.CastAs[string](args[0])
	if err != nil {
		return nil, err
	}
	return interpreter.Symbol(name), nil
}

func GenSym(args ...any) (any, error) {
	return interpreter.GenSym(), nil
}

func IsNil(args ...any) (any, error) {
	return args[0] == nil, nil
}
