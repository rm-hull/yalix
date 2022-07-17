package interpreter

import (
	"yalix/cmd/environment"

	"github.com/pkg/errors"
)

type closure struct {
	Primitive[any]
	env    environment.Env[any]
	lambda lambda
}

func Closure(env environment.Env[any], lambda lambda) closure {
	return closure{
		env:    env,
		lambda: lambda,
	}
}

func (c closure) Eval(env environment.Env[any]) (any, error) {
	return c, nil
}

func (c closure) Apply(env environment.Env[any], caller Caller) (any, error) {
	if !c.lambda.HasSufficientArity(caller.params) {
		return nil, errors.Errorf("Call to '%s' applied with insufficient arity: %d args expected, %d supplied",
			// # FIXME: probably ought rely on __repr__ of symbol here....
			caller.funexp,
			c.lambda.Arity(),
			len(caller.params))
	}
	return c, nil
}

// class Closure(Primitive):
//     """ A closure is not in 'source' programs; it is what functions evaluate to """

//     def __init__(self, env, func):
//         self.env = env
//         self.func = func

//     def eval(self, env):
//         return self

//     @classmethod
//     def bind(cls, env_to_extend, formals, params, caller_env):
//         """
//         Extend the closure's environment by binding the
//         params to the functions formals
//         """
//         for i, bind_variable in enumerate(formals):
//             if bind_variable == Lambda.VARIADIC_MARKER:  # variadic arg indicator
//                 # Use the next formal as the /actual/ bind variable,
//                 # evaluate the remaining arguments into a list (NOTE offset from i)
//                 # and dont process any more arguments
//                 bind_variable = formals[i + 1]
//                 value = List.make_lazy_list(params[i:]).eval(caller_env)
//                 env_to_extend = env_to_extend.extend(bind_variable.name, value)
//                 break
//             else:
//                 value = params[i].eval(caller_env)
//                 env_to_extend = env_to_extend.extend(bind_variable.name, value)
//         return env_to_extend

//     def apply(self, env, caller):
//         if not self.func.has_sufficient_arity(caller.params):
//             raise EvaluationError(self,
//                                   'Call to \'{0}\' applied with insufficient arity: {1} args expected, {2} supplied',
//                                   # FIXME: probably ought rely on __repr__ of symbol here....
//                                   caller.funexp.name,
//                                   self.func.arity(),
//                                   len(caller.params))

//         if not self.func.is_variadic() and len(self.func.formals) != len(caller.params):
//             raise EvaluationError(self,
//                                   'Call to \'{0}\' applied with excessive arity: {1} args expected, {2} supplied',
//                                   # FIXME: probably ought rely on __repr__ of symbol here....
//                                   caller.funexp.name,
//                                   self.func.arity(),
//                                   len(caller.params))

//         extended_env = Closure.bind(
//             self.env, self.func.formals, caller.params, env)
//         extended_env.stack_depth = env.stack_depth + 1
//         return self.func.body.eval(extended_env)
