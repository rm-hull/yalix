package ast

import (
	"strconv"
	"yalix/internal/interpreter"
	"yalix/internal/util"

	parsec "github.com/prataprc/goparsec"
)

func first(ns []parsec.ParsecNode) parsec.ParsecNode {
	if len(ns) == 0 {
		return nil
	}

	return ns[0]
}

func atomNodify(ns []parsec.ParsecNode) parsec.ParsecNode {
	node := first(ns)

	if term, err := util.CastAs[*parsec.Terminal](node); err == nil {
		switch term.Name {
		case "INT":
			i, err := strconv.Atoi(term.Value)
			if err != nil {
				panic(err)
			}
			return interpreter.Atom(i)
		case "HEX":
			i64, err := strconv.ParseInt(term.Value[2:], 16, 0)
			if err != nil {
				panic(err)
			}
			return interpreter.Atom(int(i64))
		case "NIL":
			return interpreter.Atom(nil)
		case "TRUE":
			return interpreter.Atom(true)
		case "FALSE":
			return interpreter.Atom(false)
		case "DBLQUOTESTRING":
			return interpreter.Atom(term.Value[1 : len(term.Value)-1])
		}
	}

	return nil
}

func symbolNodify(ns []parsec.ParsecNode) parsec.ParsecNode {
	node := first(ns)

	if term, err := util.CastAs[*parsec.Terminal](node); err == nil && term.Name == "SYMBOL" {
		return interpreter.Symbol(term.Value)
	}

	return nil
}

func listNodify(ns []parsec.ParsecNode) parsec.ParsecNode {
	if len(ns) != 3 {
		return nil
	}

	nodes := ns[1].([]parsec.ParsecNode)
	if len(nodes) == 0 {
		return interpreter.List()
	}

	primitives := make([]interpreter.Primitive, len(nodes))
	for i, node := range ns[1].([]parsec.ParsecNode) {
		primitives[i] = node.(interpreter.Primitive)
	}
	return interpreter.List(primitives...)
}

func quoteNodify(ns []parsec.ParsecNode) parsec.ParsecNode {
	if len(ns) != 2 {
		return nil
	}

	node := ns[1]
	return interpreter.Quote(node.(interpreter.Primitive))
}
