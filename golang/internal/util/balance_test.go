package util

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestBalance(t *testing.T) {

	testCases := map[string]struct {
		input    string
		expected int
	}{
		// empty
		"empty string": {input: "", expected: 0},

		// single parens
		"singe parens/balanced":            {input: "()", expected: 0},
		"singe parens/unbalanced":          {input: ")(", expected: -1},
		"singe parens/balanced whitespace": {input: "  ( )   ", expected: 0},
		"singe parens/balanced text":       {input: "(sfs sfsfs sdf) sfs", expected: 0},

		// unbalanced
		"unbalanced/no closing paren": {input: "(sfs sfsfs sdf sfs", expected: 1},
		"unbalanced/no opening paren": {input: "sfs sfsfs sdf sfs)", expected: -1},

		// nested parens
		"nested parens/balanced/1": {input: "(sfs (sfsfs) (sdf (sfs)))", expected: 0},
		"nested parens/balanced/2": {input: "(sfs (sfsfs (sdf (sfs))))", expected: 0},
		"nested parens/balanced/3": {input: "(((((sfs) sfsfs) sdf) sfs))", expected: 0},
		"nested parens/unbalanced": {input: "(sfs (sfsfs (sdf sfs))))", expected: -1},
	}

	for name, tc := range testCases {
		t.Run(name, func(t *testing.T) {
			require.Equal(t, tc.expected, Balance(tc.input))
		})
	}
}
