package interpreter

import (
	"fmt"
	"yalix/internal/environment"
	"yalix/internal/util"
)

type promise struct {
	BuiltIn
	closure  closure
	realized bool
	result   any
	err      error
}

func (p *promise) Eval(env environment.Env) (any, error) {
	return p, nil
}

func (p *promise) Apply(env environment.Env, caller Caller) (any, error) {
	if !p.realized {
		p.result, p.err = p.closure.Apply(env, caller)
		p.realized = true
	}

	return p.result, p.err
}

func (p *promise) String() string {
	if p.realized {
		return fmt.Sprint(p.result)
	}
	return "<unrealized>"
}

func Promise(closure closure) *promise {
	return &promise{
		closure:  closure,
		realized: false,
		result:   nil,
	}
}

func IsPromise(args ...any) (any, error) {
	_, err := util.CastAs[promise](args[0])
	return err != nil, nil
}

func IsRealized(args ...any) (any, error) {
	promise, err := util.CastAs[promise](args[0])
	if err != nil {
		return false, nil
	}
	return promise.realized, nil
}
