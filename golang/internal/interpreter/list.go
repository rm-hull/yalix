package interpreter

import (
	"fmt"
	"strings"
	"yalix/internal/environment"
	"yalix/internal/util"
)

// # http://code.activestate.com/recipes/474088/
// class List(Primitive):
//     """ A list """

//     def __init__(self, *args):
//         self.args = args
//         if args:
//             self.funexp = self.args[0]
//             self.params = self.args[1:]

//     def __repr__(self):
//         return str(self.args).replace(',', '')

//     def __len__(self):
//         return len(self.args)

//     def __iter__(self):
//         return self.args.__iter__()

//     def __getitem__(self, index):
//         return self.args.__getitem__(index)

//     def index(self, value):
//         return self.args.index(value)

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

//     def quoted_form(self, env):
//         """ Override default implementation to present as a list """
//         quote = SyntaxQuote if SyntaxQuote.ID in env else Quote
//         return List.make_lazy_list([quote(a) for a in self.splice_args(self.args, env)]).eval(env)

//     def eval(self, env):
//         if self.args:
//             value = self.funexp.eval(env)
//             if env['*debug*']:
//                 utils.debug('{0}{1} {2}', '  ' * env.stack_depth,
//                             self.funexp.name, self.params)
//             try:
//                 return value.apply(env, self)
//             except AttributeError:
//                 raise EvaluationError(
//                     self, 'Cannot invoke with: \'{0}\'', value)

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

func List(args ...Primitive) list {
	return list{
		items: args,
	}
}