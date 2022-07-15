package interpreter

import "yalix/cmd/environment"

type symbol struct {
	name string
}

func (s symbol) Eval(env environment.Env[any]) (any, error) {
	return env.Get(s.name)
}

func (s symbol) Repr() string {
	return s.name
}

func Symbol(name string) symbol {
	return symbol{name: name}
}
