package interpreter

import (
	"yalix/internal/environment"
	"yalix/internal/util"
)

type delay struct {
	BuiltIn
	body []Primitive
}

func (d delay) Eval(env environment.Env) (any, error) {
	result, err := Lambda(List(), d.body...).Eval(env)
	if err != nil {
		return nil, err
	}
	closure, err := util.CastAs[closure](result)
	if err != nil {
		return nil, err
	}

	return Promise(closure), nil
}

// Creates a promise that when forced, evaluates the body to produce its
// value. The result is then cached so that further uses of force produces
// the cached value immediately.
func Delay(body ...Primitive) delay {
	return delay{body: body}
}
