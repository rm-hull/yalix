package interpreter

import (
	"fmt"
)

type Caller struct {
	funexp Primitive[any]
	params []Primitive[any]
}

func (c Caller) String() string {
	return fmt.Sprintf("%s %s", c.funexp, c.params)
}

func MakeCaller(items ...Primitive[any]) Caller {
	return Caller{
		funexp: items[0],
		params: items[1:],
	}
}
