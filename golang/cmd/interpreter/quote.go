package interpreter

import (
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

type quote struct {
	expr Primitive[any]
}

func (q quote) Eval(env environment.Env[any]) (any, error) {
	return q.expr.QuotedForm(env)
}

func (q quote) Apply(env environment.Env[any], caller Caller[any]) (any, error) {
	return nil, errors.New("Cannot invoke with: 'Quote'")
}

func (q quote) QuotedForm(env environment.Env[any]) (any, error) {
	return q.expr, nil
}

// Makes no effort to call the supplied expression when evaluated
func Quote(expr Primitive[any]) quote {
	return quote{expr: expr}
}
