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

func NewScanner(text []byte) parsec.Scanner {
	// WSPattern also swallows comment lines (; to EOL)
	return parsec.NewScanner(text).TrackLineno().SetWSPattern(`^[ \t\r\n]*(?m:(;.*$)?[ \t\r\n]*)*`)
}

func makeParser(ast *parsec.AST) parsec.Parser {
	var expr parsec.Parser

	atom := parsec.OrdChoice(atomNodify,
		parsec.Hex(),
		parsec.Int(),
		parsec.Token("(true|#t)", "TRUE"),
		parsec.Token("(false|#f)", "FALSE"),
		parsec.Token(`"[^"]*"`, "DBLQUOTESTRING"),
		parsec.Token("([a-z0-9-/_:*+=!?<>.]+|λ)", "SYMBOL"),
	)

	list := parsec.And(listNodify,
		parsec.Atom("(", "LPAREN"),
		parsec.Kleene(nil, &expr),
		parsec.Atom(")", "RPAREN"),
	)

	quote := parsec.And(quoteNodify, parsec.Atom("'", "QUOTE"), &expr)

	expr = parsec.OrdChoice(first, atom, list, quote)

	return parsec.And(first, parsec.Kleene(nil, expr), eof())
}

func eof() parsec.Parser {
	return func(s parsec.Scanner) (parsec.ParsecNode, parsec.Scanner) {
		_, news := s.SkipWS()
		if news.Endof() {
			return parsec.NewTerminal("EOF", "", news.GetCursor()), news
		}
		return nil, news
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
