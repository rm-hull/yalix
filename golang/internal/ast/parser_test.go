package ast

import (
	"testing"
	"yalix/internal/interpreter"

	"github.com/stretchr/testify/require"
)

func Test_Parser(t *testing.T) {
	parser := SchemeParser(true)

	testCases := map[string]struct {
		input    string
		expected interpreter.Primitive
	}{
		// Atoms
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
		"symbol/nil":                {input: `nil`, expected: interpreter.Symbol("nil")},
		"symbol/ascii":              {input: `cadr`, expected: interpreter.Symbol("cadr")},
		"symbol/with punctuation/1": {input: `digit?`, expected: interpreter.Symbol("digit?")},
		"symbol/with punctuation/2": {input: `transform*`, expected: interpreter.Symbol("transform*")},
		"symbol/with punctuation/3": {input: `+`, expected: interpreter.Symbol("+")},
		"symbol/with keyword":       {input: `:red`, expected: interpreter.Symbol(":red")},
		"symbol/with hyphen":        {input: `hair-color`, expected: interpreter.Symbol("hair-color")},
		"symbol/lambda alias":       {input: `λ`, expected: interpreter.Symbol("λ")},

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
	}

	for name, tc := range testCases {
		t.Run(name, func(t *testing.T) {
			text := []byte(tc.input)
			node, _ := parser(NewScanner(text))

			if tc.expected == nil {
				require.Nil(t, node)
			} else {
				require.NotNil(t, node)
				primitives, err := ToPrimitives(node)
				require.Nil(t, err)
				require.Equal(t, 1, len(*primitives))
				require.Equal(t, tc.expected, (*primitives)[0])
			}
		})
	}
}

func TestComments(t *testing.T) {
	parser := SchemeParser(true)
	text := []byte(`
	
	(hello 
		1 
		; comment1
		2 
		3) ; comment2
	; comment3
	world
	
	;;;;;;;;;;;;
	; comment4 ;
	; comment5 ;
	;;;;;;;;;;;;
	`)
	node, _ := parser(NewScanner(text))

	require.NotNil(t, node)
	primitives, err := ToPrimitives(node)
	require.Nil(t, err)
	expected := []interpreter.Primitive{
		interpreter.List(
			interpreter.Symbol("hello"),
			interpreter.Atom(1),
			interpreter.Atom(2),
			interpreter.Atom(3),
		),
		interpreter.Symbol("world"),
	}
	require.Equal(t, &expected, primitives)
}
