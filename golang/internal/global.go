package internal

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"yalix/internal/ast"
	"yalix/internal/environment"
	"yalix/internal/interpreter"
	"yalix/internal/operator"
	"yalix/internal/util"

	"github.com/pkg/errors"
)

var CORE_LIBRARIES = []string{"core", "hof", "num", "macros", "repr", "test"}

func BootstrapSpecialForms(env *environment.Env) {
	for name := range interpreter.SPECIAL_FORMS {
		env.SetGlobal(name, interpreter.SpecialForm(name))
	}
}

func BootstrapNativeFunctions(env *environment.Env) error {
	env.SetGlobal("*debug*", false)
	functions := map[string]interpreter.Primitive{
		"atom?": interpreter.MakeGoFuncHandler(operator.IsNil, 1, false),

		// Basic Arithmetic Functions
		"+": interpreter.MakeGoFuncHandler(operator.Add, 1, true),
		"-": interpreter.MakeGoFuncHandler(operator.Sub, 1, true),
		"*": interpreter.MakeGoFuncHandler(operator.Mult, 1, true),
		"/": interpreter.MakeGoFuncHandler(operator.Div, 1, true),

		// Comparison & Ordering
		"=": interpreter.MakeGoFuncHandler(operator.Eq, 1, true),
	}

	for name, lambda := range functions {
		closure, err := lambda.Eval(*env)
		if err != nil {
			return err
		}

		env.SetGlobal(name, closure)
	}

	return nil
}

func BootstrapLispFunctions(env *environment.Env, module string) error {
	_, filename, _, ok := runtime.Caller(0)
	if !ok {
		return errors.New("unable to get the current filename")
	}
	dirname := filepath.Dir(filename)

	absPath, err := filepath.Abs(fmt.Sprintf("%s/../../core/%s.ylx", dirname, module))
	if err != nil {
		return err
	}

	data, err := os.ReadFile(absPath)
	if err != nil {
		return err
	}

	_, err = eval(env, string(data))
	if err != nil {
		return err
	}

	return nil
}

func CreateInitialEnv() (*environment.Env, error) {
	env := environment.MakeEnv()

	err := util.LogProgress("Creating initial environment", func() error {
		BootstrapSpecialForms(&env)
		return BootstrapNativeFunctions(&env)
	})
	if err != nil {
		return nil, err
	}

	for _, module := range CORE_LIBRARIES {
		err := util.LogProgress("Loading library: "+module, func() error {
			return BootstrapLispFunctions(&env, module)
		})
		if err != nil {
			return nil, err
		}
	}

	return &env, nil
}

func eval(env *environment.Env, data string) (any, error) {
	parser := ast.SchemeParser(true)
	scanner := ast.NewScanner([]byte(data))
	node, news := parser(scanner)

	primitives, err := ast.ToPrimitives(node)
	if err != nil {
		return nil, err
	}

	if !news.Endof() {
		return nil, errors.Errorf("failed to parse line %d, position %d\n\n%s", news.Lineno(), news.GetCursor(), data)
	}

	var result any
	for _, primitive := range *primitives {
		result, err = primitive.Eval(*env)
		if err != nil {
			return nil, err
		}
	}
	return result, nil
}

// def bootstrap_python_functions(env):
//     env = EvalWrapper(env)

//     env['*debug*'] = Atom(False)
//     env['nil'] = Atom(None)
//     env['nil?'] = interop(lambda x: x is None, 1)
//     env['atom?'] = interop(atom_QUESTION, 1)
//     env['pair?'] = interop(pair_QUESTION, 1)
//     env['promise?'] = interop(promise_QUESTION, 1)
//     env['realized?'] = interop(realized_QUESTION, 1)
//     env['cons'] = interop(lambda x, y: (x, y), 2)
//     env['car'] = interop(car, 1)
//     env['cdr'] = interop(cdr, 1)
//     env['gensym'] = interop(gensym, 0)
//     env['symbol'] = interop(lambda x: Symbol(x), 1)
//     env['symbol?'] = interop(lambda x: isinstance(x, Symbol), 1)
//     env['interop'] = interop(interop, 2)
//     env['doc'] = interop(doc, 1)
//     env['source'] = interop(source, 1)
//     env['print'] = interop(print_, 1, variadic=True)
//     env['format'] = interop(format_, 2, variadic=True)
//     env['str'] = interop(str_, 1, variadic=True)
//     env['read-string'] = interop(read_string, 1)  # Read just one symbol
//     env['error'] = interop(error, 1)
//     env['epoch-time'] = interop(time.time, 0)

//     # Basic Arithmetic Functions
//     env['add'] = interop(operator.add, 2)
//     env['sub'] = interop(operator.sub, 2)
//     env['mul'] = interop(operator.mul, 2)
//     env['div'] = interop(operator.truediv, 2)
//     env['quot'] = interop(operator.floordiv, 2)
//     env['negate'] = interop(operator.neg, 1)

//     # String / Sequence Functions
//     env['contains?'] = interop(operator.contains, 2)

//     # Bitwise Ops
//     env['bitwise-and'] = interop(operator.and_, 2)
//     env['bitwise-xor'] = interop(operator.xor, 2)
//     env['bitwise-invert'] = interop(operator.invert, 2)
//     env['bitwise-or'] = interop(operator.or_, 2)
//     env['bitwise-and'] = interop(operator.and_, 2)
//     env['bitwise-left-shift'] = interop(operator.lshift, 2)
//     env['bitwise-right-shift'] = interop(operator.rshift, 2)

//     env['not'] = interop(operator.not_, 1)

//     # Comparison & Ordering
//     env['not='] = interop(operator.ne, 2)
//     env['<'] = interop(operator.lt, 2)
//     env['<='] = interop(operator.le, 2)
//     env['='] = interop(operator.eq, 2)
//     env['>='] = interop(operator.ge, 2)
//     env['>'] = interop(operator.gt, 2)

//     env['random'] = interop(random.random, 0)

//     # Number theoretic Functions
//     env['ceil'] = interop(math.ceil, 1)
//     env['floor'] = interop(math.floor, 1)
//     env['mod'] = interop(operator.mod, 2)
//     env['trunc'] = interop(math.trunc, 1)

//     # Power & Logarithmic Functions
//     env['exp'] = interop(math.exp, 1)
//     env['log'] = interop(math.log, 2)
//     env['log10'] = interop(math.log10, 1)
//     env['pow'] = interop(math.pow, 2)
//     env['sqrt'] = interop(math.sqrt, 1)

//     # Trigonomeric Functions
//     env['acos'] = interop(math.acos, 1)
//     env['asin'] = interop(math.asin, 1)
//     env['atan'] = interop(math.atan, 1)
//     env['atan2'] = interop(math.atan2, 1)
//     env['cos'] = interop(math.cos, 1)
//     env['hypot'] = interop(math.hypot, 2)
//     env['sin'] = interop(math.sin, 1)
//     env['tan'] = interop(math.tan, 1)

//     # Angular Conversion
//     env['degrees'] = interop(math.degrees, 1)
//     env['radians'] = interop(math.radians, 1)

//     # Hyperbolic Functions
//     env['acosh'] = interop(math.acosh, 1)
//     env['asinh'] = interop(math.asinh, 1)
//     env['atanh'] = interop(math.atanh, 1)
//     env['cosh'] = interop(math.cosh, 1)
//     env['sinh'] = interop(math.sinh, 1)
//     env['tanh'] = interop(math.tanh, 1)

//     # Constants
//     env['math/pi'] = Atom(math.pi)
//     env['math/e'] = Atom(math.e)
