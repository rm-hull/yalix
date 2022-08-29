package util

// Checks whether the parens in the text are balanced. If the return result is:
//   - zero: balanced
//   - negative: too many right parens
//   - positive: too many left parens
func Balance(text string) int {
	return bal(text, 0)
}

func bal(text string, count int) int {
	if text == "" {
		return count
	} else if text[0] == '(' && count >= 0 {
		return bal(text[1:], count+1)
	} else if text[0] == ')' {
		return bal(text[1:], count-1)
	} else {
		return bal(text[1:], count)
	}
}
