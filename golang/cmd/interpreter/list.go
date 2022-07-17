package interpreter

import (
	"fmt"
	"strings"
	"yalix/cmd/environment"
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
	Primitive[any]
	items []Primitive[any]
}

func (l list) Eval(env environment.Env[any]) (any, error) {
	if len(l.items) > 0 {
		funexp := l.items[0]
		params := l.items[1:]
		value, err := funexp.Eval(env)
		if err != nil {
			return nil, err
		}
		if debug, err := env.Get("*debug*"); err == nil && debug.(bool) {
			fmt.Printf("%s%s %s\n", strings.Repeat(" ", env.StackDepth()), funexp, params)
		}
		return value.(Primitive[any]).Apply(env, MakeCaller(l.items...))
	}
	return nil, nil
}

func (l list) Len() int {
	return len(l.items)
}

func List(args ...Primitive[any]) list {
	return list{
		items: args,
	}
}
