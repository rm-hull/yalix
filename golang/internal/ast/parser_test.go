package ast

import (
	"testing"
	"yalix/internal/interpreter"

	parsec "github.com/prataprc/goparsec"
	"github.com/stretchr/testify/require"
)

func Test_Parser(t *testing.T) {
	parser := SchemeParser(true)

	testCases := map[string]struct {
		input    string
		expected interpreter.Primitive
	}{
		// Atoms
		"atom/nil":                 {input: `nil`, expected: interpreter.Atom(nil)},
		"atom/integer":             {input: "17", expected: interpreter.Atom(17)},
		"atom/hex":                 {input: "0x17", expected: interpreter.Atom(23)},
		"atom/bool/#t":             {input: `#t`, expected: interpreter.Atom(true)},
		"atom/bool/#f":             {input: `#f`, expected: interpreter.Atom(false)},
		"atom/bool/true":           {input: `true`, expected: interpreter.Atom(true)},
		"atom/bool/false":          {input: `false`, expected: interpreter.Atom(false)},
		"atom/string/empty":        {input: `""`, expected: interpreter.Atom("")},
		"atom/string/simple":       {input: `"hello"`, expected: interpreter.Atom("hello")},
		"atom/string/unterminated": {input: `"hello`, expected: nil},
		"atom/string/unicode":      {input: `"hello 🌎"`, expected: interpreter.Atom("hello 🌎")},

		// Symbols
		"symbol/ascii":              {input: `cadr`, expected: interpreter.Symbol("cadr")},
		"symbol/with punctuation/1": {input: `digit?`, expected: interpreter.Symbol("digit?")},
		"symbol/with punctuation/2": {input: `transform*`, expected: interpreter.Symbol("transform*")},
		"symbol/with punctuation/3": {input: `+`, expected: interpreter.Symbol("+")},
		"symbol/with keyword":       {input: `:red`, expected: interpreter.Symbol(":red")},
		"symbol/with hyphen":        {input: `hair-color`, expected: interpreter.Symbol("hair-color")},

		// Lists
		"list/empty":      {input: `()`, expected: interpreter.List()},
		"list/simple":     {input: `(+ 1 2)`, expected: interpreter.List(interpreter.Symbol("+"), interpreter.Atom(1), interpreter.Atom(2))},
		"list/unbalanced": {input: `(1 2`, expected: nil},
		"list/nested": {input: `(+ 2 (* (- 5 4) 6))`, expected: interpreter.List(
			interpreter.Symbol("+"),
			interpreter.Atom(2),
			interpreter.List(
				interpreter.Symbol("*"),
				interpreter.List(
					interpreter.Symbol("-"),
					interpreter.Atom(5),
					interpreter.Atom(4),
				),
				interpreter.Atom(6),
			),
		)},

		// Quote
		"quote/atom": {input: `'hello`, expected: interpreter.Quote(interpreter.Symbol("hello"))},
		"quote/list": {input: `'(1 2 'hello)`, expected: interpreter.Quote(
			interpreter.List(
				interpreter.Atom(1),
				interpreter.Atom(2),
				interpreter.Quote(interpreter.Symbol("hello")),
			),
		)},

		// Comments
		// "comment/1": {input: `; this is a comment`, expected: nil},
		// "comment/2": {input: `; this is a comment\nhello`, expected: interpreter.Symbol("hello")},
		// "comment/3": {input: `hello ; this is a comment\nworld`, expected: interpreter.Symbol("hello")},
	}

	for name, tc := range testCases {
		t.Run(name, func(t *testing.T) {
			data := []byte(tc.input)
			scanner := parsec.NewScanner(data).TrackLineno()
			node, _ := parser(scanner)

			if tc.expected == nil {
				require.Nil(t, node)
			} else {
				primitives, err := ToPrimitives(node)
				require.Nil(t, err)
				require.Equal(t, tc.expected, (*primitives)[0])
			}
		})
	}
}
