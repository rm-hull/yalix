package interpreter

type Caller[T any] struct {
	funexp Primitive[T]
	params []T
}

func MakeCaller[T any](funexp Primitive[T], params ...T) Caller[T] {
	return Caller[T]{
		funexp: funexp,
		params: params,
	}
}
