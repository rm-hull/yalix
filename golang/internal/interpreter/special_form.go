package interpreter

import (
	"fmt"
	"yalix/internal/environment"

	"github.com/pkg/errors"
)

var SPECIAL_FORMS = map[string]func(params ...Primitive) (Primitive, error){
	"symbol": func(params ...Primitive) (Primitive, error) {
		// TODO: Add error handling
		return Symbol(fmt.Sprint(params[0])), nil
	},
	"quote": func(params ...Primitive) (Primitive, error) {
		// TODO: Add error handling
		return Quote(params[0]), nil
	},
	"lambda": func(params ...Primitive) (Primitive, error) {
		// TODO: Add error handling
		return Lambda(params[0].(list), params[1:]...), nil
	},
	"begin": func(params ...Primitive) (Primitive, error) {
		// TODO: Add error handling
		return Body(params...), nil
	},
	"if": func(params ...Primitive) (Primitive, error) {
		// TODO: Add error handling
		if len(params) == 2 {
			return If(params[0], params[1], NIL), nil
		}
		return If(params[0], params[1], params[2]), nil
	},
	"let": func(params ...Primitive) (Primitive, error) {
		// TODO: Add error handling
		return Let(params[0].(list), params[1:]...), nil
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
	Primitive
	name string
	impl func(params ...Primitive) (Primitive, error)
}

// A proxy for other built-in types
func SpecialForm(name string) specialForm {
	return specialForm{
		name: name,
		impl: SPECIAL_FORMS[name],
	}
}

func (sf specialForm) Eval(env environment.Env) (any, error) {
	return sf, nil
}

func (sf specialForm) Apply(env environment.Env, caller Caller) (any, error) {
	if sf.impl == nil {
		return nil, errors.Errorf("Unknown special form: '%s'", sf.name)
	}
	form, err := sf.impl(caller.params...)
	if err != nil {
		return nil, err
	}
	return form.Eval(env)
}

func (sf specialForm) QuotedForm(env environment.Env) (any, error) {
	return sf.Eval(env)
}
