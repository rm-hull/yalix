package interpreter

type Caller struct {
	funexp Primitive[any]
	params []Primitive[any]
}

func MakeCaller(items ...Primitive[any]) Caller {
	return Caller{
		funexp: items[0],
		params: items[1:],
	}
}
