class EvaluationError(StandardError):
     def __init__(self, message, *args):
        self.value = message.format(*args)

     def __str__(self):
        return repr(self.value)

