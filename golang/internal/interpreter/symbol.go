package interpreter

import (
	"fmt"
	"strings"
	"yalix/internal/environment"
	"yalix/internal/util"

	"github.com/pkg/errors"
)

type symbol struct {
	BuiltIn
	name string
}

func (s symbol) Eval(env environment.Env) (any, error) {
	return env.Get(s.name)
}

func (s symbol) Apply(env environment.Env, caller Caller) (any, error) {
	return nil, errors.Errorf("cannot invoke with: '%s'", s)
}

func (s symbol) String() string {
	return s.name
}

func (s symbol) Repr() string {
	return s.name
}

func (s symbol) QuotedForm(env environment.Env) (any, error) {
	if strings.HasSuffix(s.name, "#") {
		uniqueId, err := env.Get(SYNTAX_QUOTE_ID)
		if err != nil {
			return nil, err
		}
		name := fmt.Sprintf("%s__%d__auto__", strings.TrimSuffix(s.name, "#"), uniqueId)
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

func IsSymbol(args ...any) (any, error) {
	_, err := util.CastAs[symbol](args[0])
	return err != nil, nil
}
