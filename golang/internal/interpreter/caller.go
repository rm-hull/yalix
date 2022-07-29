package interpreter

type Caller struct {
	funexp Primitive
	params []Primitive
}

func MakeCaller(items ...Primitive) Caller {
	return Caller{
		funexp: items[0],
		params: items[1:],
	}
}
