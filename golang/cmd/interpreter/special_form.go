package interpreter

import (
	"fmt"
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

var SPECIAL_FORMS = map[string]func(params ...Primitive[any]) Primitive[any]{
	"symbol": func(params ...Primitive[any]) Primitive[any] {
		return Symbol(fmt.Sprint(params[0]))
	},
	"quote": func(params ...Primitive[any]) Primitive[any] {
		return Quote(params[0])
	},
	"lambda": func(params ...Primitive[any]) Primitive[any] {
		return Lambda(params[0].(list), params[1:]...)
	},
	"begin": func(params ...Primitive[any]) Primitive[any] {
		return Body(params...)
	},
	"if": func(params ...Primitive[any]) Primitive[any] {
		if len(params) == 2 {
			return If(params[0], params[1], NIL)
		}
		return If(params[0], params[1], params[2])
	},
	"let": func(params ...Primitive[any]) Primitive[any] {
		return Let(params[0].(list), params[1:]...)
	},
}

// __special_forms__ = {
//  'symbol': Symbol,
// 	'quote': Quote,
// 	'lambda': Lambda,
// 	'λ': Lambda,
// 	'define': Define,
// 	'begin': Body,
// 	'if': If,
// 	'let': Let,
// 	'let*': Let_STAR,
// 	'letrec': LetRec,
// 	'set!': Set_PLING,
// 	'delay': Delay,
// 	'eval': Eval
// }

type specialForm struct {
	Primitive[any]
	name string
	impl func(params ...Primitive[any]) Primitive[any]
}

// A proxy for other built-in types
func SpecialForm(name string) specialForm {
	return specialForm{
		name: name,
		impl: SPECIAL_FORMS[name],
	}
}

func (sf specialForm) Eval(env environment.Env[any]) (any, error) {
	return sf, nil
}

func (sf specialForm) Apply(env environment.Env[any], caller Caller) (any, error) {
	if sf.impl == nil {
		return nil, errors.Errorf("Unknown special form: '%s'", sf.name)
	}
	return sf.impl(caller.params...).Eval(env)
}

func (sf specialForm) QuotedForm(env environment.Env[any]) (any, error) {
	return sf.Eval(env)
}
