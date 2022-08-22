package ast

import (
	"yalix/internal/interpreter"
	"yalix/internal/util"

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
		parsec.Token("[a-z0-9-/_:*+=!?<>.]+", "SYMBOL"),
	)

	list := parsec.And(listNodify,
		parsec.Atom("(", "LPAREN"),
		parsec.Kleene(nil, &expr),
		parsec.Atom(")", "RPAREN"),
	)

	quote := parsec.And(quoteNodify, parsec.Atom("'", "QUOTE"), &expr)

	expr = parsec.OrdChoice(first, atom, list, quote, comment())

	return parsec.And(first, parsec.Kleene(nil, expr), ast.End("EOF"))
}

func comment() parsec.Parser {
	return func(s parsec.Scanner) (parsec.ParsecNode, parsec.Scanner) {
		_, s = s.SkipAny(`;[^^].*`)
		return nil, s
	}
}

func ToPrimitives(node parsec.ParsecNode) (*[]interpreter.Primitive, error) {
	if node == nil {
		return nil, nil
	}

	nodes, err := util.CastAs[[]parsec.ParsecNode](node)
	if err != nil {
		return nil, err
	}

	var primitives = make([]interpreter.Primitive, len(nodes))
	for i, node := range nodes {
		prim, err := util.CastAs[interpreter.Primitive](node)
		if err != nil {
			return nil, err
		}
		primitives[i] = prim
	}
	return &primitives, nil
}
