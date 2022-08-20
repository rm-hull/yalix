package interpreter

import (
	"yalix/internal/environment"
)

const SYNTAX_QUOTE_ID = "G__syntax_quote_id"

type syntaxQuote struct {
	quote
	expr Primitive
}

func (sq syntaxQuote) Eval(env environment.Env) (any, error) {
	if !env.Includes(SYNTAX_QUOTE_ID) {
		env = env.Extend(SYNTAX_QUOTE_ID, environment.NextId())
	}
	return sq.expr.QuotedForm(env)
}

func SyntaxQuote(expr Primitive) syntaxQuote {
	return syntaxQuote{expr: expr}
}
