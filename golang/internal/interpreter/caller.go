package interpreter

type Caller struct {
	funexp Primitive
	params []Primitive
}

func MakeCaller(items ...Primitive) Caller {
	if len(items) < 1 {
		panic("MakeCaller() expects 1 or more constructor parameters")
	}
	return Caller{
		funexp: items[0],
		params: items[1:],
	}
}
