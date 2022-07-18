package interpreter

import (
	"fmt"
	"strings"
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

type symbol struct {
	BuiltIn[any]
	name string
}

func (s symbol) Eval(env environment.Env[any]) (any, error) {
	return env.Get(s.name)
}

func (s symbol) Apply(env environment.Env[any], caller Caller) (any, error) {
	return nil, errors.Errorf("cannot invoke with: '%s'", s)
}

func (s symbol) String() string {
	return s.name
}

func (s symbol) Repr() string {
	return s.name
}

func (s symbol) QuotedForm(env environment.Env[any]) (any, error) {
	if strings.HasSuffix(s.name, "#") && env.Includes(SYNTAX_QUOTE_ID) {
		uniqueId, err := env.Get(SYNTAX_QUOTE_ID)
		if err != nil {
			return nil, err
		}
		name := fmt.Sprintf("%s__%s__auto__", strings.TrimSuffix(s.name, "#"), uniqueId)
		return Symbol(name), nil
	}
	return s, nil
}

// A symbolic reference, resolved in the environment firstly against lexical
// closures in local symbol stack, then against a global symbol table.
func Symbol(name string) symbol {
	return symbol{name: name}
}

func GenSym() symbol {
	return Symbol(fmt.Sprintf("G__%d", environment.NextId()))
}
