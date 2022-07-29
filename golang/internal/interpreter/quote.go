package interpreter

import (
	"fmt"
	"yalix/internal/environment"

	"github.com/pkg/errors"
)

type quote struct {
	Primitive
	expr Primitive
}

func (q quote) Eval(env environment.Env) (any, error) {
	return q.expr.QuotedForm(env)
}

func (q quote) Apply(env environment.Env, caller Caller) (any, error) {
	return nil, errors.Errorf("cannot invoke with: '%s'", q)
}

func (q quote) QuotedForm(env environment.Env) (any, error) {
	return q.expr, nil
}

func (q quote) Repr() string {
	return q.expr.Repr()
}

func (q quote) String() string {
	return fmt.Sprint(q.expr)
}

// Makes no effort to call the supplied expression when evaluated
func Quote(expr Primitive) quote {
	return quote{expr: expr}
}
