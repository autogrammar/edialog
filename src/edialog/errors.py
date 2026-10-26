class EDialogError(ValueError):
    """Base error. Input is never silently reduced to a partially matched request."""


class ValidationError(EDialogError):
    pass


class NeedsClarification(EDialogError):
    pass


class UnsupportedObjective(EDialogError):
    pass


class BackendError(EDialogError):
    pass
