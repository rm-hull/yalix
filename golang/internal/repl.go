package internal

import (
	"fmt"
	"runtime"
	"sort"
	"strings"
	"time"
	"yalix/internal/environment"
	"yalix/internal/util"

	"runtime/debug"

	"github.com/chzyer/readline"
	"github.com/fatih/color"
)

func Repl() {

	env, err := CreateInitialEnv()
	if err != nil {
		panic(err)
	}

	env.SetGlobal("copyright", copyright())
	env.SetGlobal("license", license())
	env.SetGlobal("help", help())
	env.SetGlobal("credits", credits())

	l, err := initReadline(env)
	if err != nil {
		panic(err)
	}
	defer l.Close()

	ready()

	var count = 1
	for {
		text, err := read(l, count)
		if err != nil {
			panic(err)
		}
		result, err := eval(env, text)
		print(result, err)

		count += 1
	}
}

var bold = color.New(color.Bold).SprintFunc()

func copyright() string {
	return fmt.Sprintf(`
Copyright (c) %d Richard Hull.
All Rights Reserved.`, time.Now().Year())
}

func license() string {
	return fmt.Sprintf(`
The MIT License (MIT)

Copyright (c) %d Richard Hull

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.`, time.Now().Year())
}

func help() string {
	return `
Yalix is a LISP interpreter: it's dialect most closely resembles that of Racket
or PLT-Scheme. This particular implementation is written in Python, and serves
as a reference implementation only. It is subject to on-going development, and
as such will suffer breaking changes, as well as being buggy and not having
been optimised. It is therefore not recommended for production use.

The main purpose of this software is to provide a pedagogical experience in
writing a LISP interpreter and a core library of functions, in a number of
different computer languages. The intention is that there will eventually be
"Seven LISPs in seven languages", where each implementation is idiomatic in
the target language. Although not fully decided, the languages will most
likely be: Python, Lua, Go/Rust, Java/Scala, Haskell/Idris, Forth, and course
there really needs to be a Yalix implementation too!

The REPL that you are now connected to has readline capabilities, and stores
a history in ~/.yalix-history. Pressing <TAB> on a partially typed word will
interrogate the environment for matching definitions and will present a word
completion facility.

Documentation for a particular function (e.g. first) can be found by evaluating
the following S-Exp at the prompt:

    (doc map)

The source code for a previously defined function will be shown when the
following is entered at the prompt (Note: special forms will not show any
source):

    (source map)

See https://github.com/rm-hull/yalix/ for further information.`
}

func credits() string {
	return `
TBD`
}

func ready() {
	fmt.Printf("%s on %s %s (%s)\n", bold("Yalix ", commit()), runtime.Version(), runtime.GOOS, runtime.GOARCH)
	fmt.Println(`Type "help", "copyright", "credits" or "license" for more information.`)
}

func initReadline(env *environment.Env) (*readline.Instance, error) {
	envCompleter := func(prefix string) []string {
		matches := *env.GlobalMatches(prefix)
		sort.Strings(matches)
		return matches
	}
	completer := readline.NewPrefixCompleter(readline.PcItemDynamic(envCompleter))

	l, err := readline.NewEx(&readline.Config{
		HistoryFile:     "/tmp/readline.tmp",
		AutoComplete:    completer,
		InterruptPrompt: "^C",
		EOFPrompt:       "exit",

		HistorySearchFold: true,
		// FuncFilterInputRune: filterInput,
	})
	if err != nil {
		return nil, err
	}
	l.CaptureExitSignal()

	return l, nil
}

func commit() string {
	if info, ok := debug.ReadBuildInfo(); ok {
		for _, setting := range info.Settings {
			if setting.Key == "vcs.revision" {
				return setting.Value
			}
		}
	}
	return version()
}

func version() string {
	return "0.0.1"
}

func read(l *readline.Instance, count int) (string, error) {
	primaryPrompt := fmt.Sprint(color.GreenString("In ["), color.HiGreenString("%s", bold(count)), color.GreenString("]: "))
	secondaryPrompt := color.GreenString("%s  ...: ", strings.Repeat(" ", len(fmt.Sprint(count))))
	l.SetPrompt(primaryPrompt)

	// var prefill = ""
	var entry = ""
	for {
		line, err := l.Readline()
		if err != nil {
			return "", err
		}
		entry += fmt.Sprintln(line)
		l.SetPrompt(secondaryPrompt)
		parensCount := util.Balance(entry)
		if parensCount > 0 {
			// prefill = strings.Repeat("  ", parensCount)
		} else {
			return entry, nil
		}
	}
}

func print(result any, err error) {
	if err != nil {
		// FIXME: handle properly
		panic(err)
	}
	fmt.Println(result)
}
