package util

import (
	"fmt"

	"github.com/fatih/color"
)

var faint = color.New(color.Faint).SprintFunc()
var bold = color.New(color.Bold).SprintFunc()

func LogProgress(message string, block func() error) error {

	fmt.Print(faint(message, " ... "))
	err := block()

	if err == nil {
		fmt.Println(bold(color.GreenString("DONE")))
	} else {
		fmt.Println(bold(color.RedString("FAILED")))
	}

	return err
}
