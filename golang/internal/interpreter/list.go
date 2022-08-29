package interpreter

import (
	"fmt"
	"strings"
	"yalix/internal/environment"
	"yalix/internal/util"
)

type list struct {
	Primitive
	items []Primitive
}

func (l list) Eval(env environment.Env) (any, error) {
	if len(l.items) > 0 {
		if debug, err := env.Get("*debug*"); err == nil && debug.(bool) {
			fmt.Printf("%s%s\n", strings.Repeat("  ", env.StackDepth()), l)
		}

		caller := MakeCaller(l.items...)
		value, err := caller.funexp.Eval(env)
		if err != nil {
			return nil, err
		}

		primitive, err := util.CastAs[Primitive](value)
		if err != nil {
			return nil, err
		}
		return primitive.Apply(env, caller)
	}
	return nil, nil
}

func (l list) Len() int {
	return len(l.items)
}

func (l list) Includes(item Primitive) bool {
	return l.Index(item) >= 0
}

func (l list) Index(item Primitive) int {
	for index, elem := range l.items {
		if item == elem {
			return index
		}
	}
	return -1
}

func (l list) Count(item Primitive) int {
	var count = 0
	for _, elem := range l.items {
		if item == elem {
			count++
		}
	}
	return count
}

func (l list) String() string {
	var sb strings.Builder
	sb.WriteByte('(')
	for index, item := range l.items {
		sb.WriteString(fmt.Sprint(item))
		if index < l.Len()-1 {
			sb.WriteByte(' ')
		}
	}
	sb.WriteByte(')')
	return sb.String()
}

//     @classmethod
//     def make_lazy_list(cls, arr):
//         t = Atom(None)
//         while arr:
//             t = List(Symbol('cons'), arr[-1], Delay(t))
//             arr = arr[:-1]
//         return t

//     def splice_args(self, args, env):
//         for arg in args:
//             if isinstance(arg, UnquoteSplice):
//                 for elem in self.splice_args(arg.eval(env), env):
//                     yield elem
//             else:
//                 yield arg

// def quoted_form(self, env):
// """ Override default implementation to present as a list """
// quote = SyntaxQuote if SyntaxQuote.ID in env else Quote
// return List.make_lazy_list([quote(a) for a in self.splice_args(self.args, env)]).eval(env)

func (l list) QuotedForm(env environment.Env) (any, error) {
	useSyntaxQuote := env.Includes(SYNTAX_QUOTE_ID)
	quoted := make([]Primitive, l.Len())
	for i, item := range l.items {
		if useSyntaxQuote {
			quoted[i] = SyntaxQuote(item)
		} else {
			quoted[i] = Quote(item)
		}
	}
	return List(quoted...), nil
}

func List(args ...Primitive) list {
	return list{
		items: args,
	}
}
