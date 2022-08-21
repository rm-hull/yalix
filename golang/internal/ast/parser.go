package ast

import (
	parsec "github.com/prataprc/goparsec"
)

func SchemeParser(debug bool) parsec.Parser {
	ast := parsec.NewAST("scheme", 100)
	if debug {
		ast.SetDebug()
	}

	return makeParser(ast)
}

func makeParser(ast *parsec.AST) parsec.Parser {
	var expr parsec.Parser

	atom := parsec.OrdChoice(atomNodify,
		parsec.Hex(),
		parsec.Int(),
		parsec.Token("(true|#t)", "TRUE"),
		parsec.Token("(false|#f)", "FALSE"),
		parsec.Token(`"[^"]*"`, "DBLQUOTESTRING"),
		parsec.Atom("nil", "NIL"),
	)

	symbol := parsec.OrdChoice(symbolNodify,
		parsec.Token("[a-z0-9-/_:*+=!?<>.]+", "SYMBOL"),
	)

	list := parsec.And(listNodify,
		parsec.Atom("(", "LPAREN"),
		parsec.Kleene(nil, &expr),
		parsec.Atom(")", "RPAREN"),
	)

	quote := parsec.And(quoteNodify, parsec.Atom("'", "QUOTE"), &expr)

	expr = parsec.OrdChoice(first, atom, symbol, list, quote)

	// TODO: return parsec.Kleene(nil, expr)
	// For now, just return a single expression
	return expr
}
