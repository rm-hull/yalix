package interop

import "yalix/internal/types"

func Overload(fns ...types.InterOpFunc) types.InterOpFunc {
	return func(args ...any) (any, error) {

		var lastErr error
		for _, fn := range fns {
			result, err := fn(args...)
			if err == nil {
				return result, nil
			}
			lastErr = err
		}
		return nil, lastErr
	}
}
