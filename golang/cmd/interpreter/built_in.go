package interpreter

type BuiltIn[T any] interface {
	Primitive[T]
}
