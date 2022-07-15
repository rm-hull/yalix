package interpreter

type Caller[T any] struct {
	funexp string
	params []T
}

func MakeCaller[T any](funexp string, params ...T) Caller[T] {
	return Caller[T]{
		funexp: funexp,
		params: params,
	}
}
