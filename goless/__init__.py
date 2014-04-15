import stackless as _stackless


from .channels import chan
from .select import dcase, rcase, scase, select


def go(func):
    """Run a function in a new tasklet, like a goroutine."""
    _stackless.tasklet(func)()
