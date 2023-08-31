import subprocess
from sceptre.hooks import Hook
from sceptre.exceptions import InvalidHookArgumentTypeError


class Cmd(Hook):
    """
    Cmd implements a Sceptre hook which can run arbitrary commands.
    """

    def __init__(self, *args, **kwargs):
        super(Cmd, self).__init__(*args, **kwargs)

    def run(self):
        """
        Runs the argument string in a subprocess.

        :raises: sceptre.exceptions.InvalidTaskArgumentTypeException
        :raises: subprocess.CalledProcessError
        """
        envs = self.stack.connection_manager.create_session_environment_variables()

        if isinstance(self.argument, str) and self.argument != "":
            args = self.argument
            executable = None
        elif (
            isinstance(self.argument, dict)
            and set(self.argument) == {"args", "executable"}
            and isinstance(self.argument["args"], str)
            and isinstance(self.argument["executable"], str)
        ):
            args = self.argument["args"]
            executable = self.argument["executable"]
        else:
            raise InvalidHookArgumentTypeError(
                "A cmd hook requires either a string argument or an object with "
                "args and executable keys with string values. "
                f"You gave {self.argument!r}."
            )

        subprocess.check_call(args, shell=True, env=envs, executable=executable)
