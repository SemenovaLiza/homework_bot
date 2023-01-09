class VariableNotFoundError(Exception):
    """Occurs when environment variables are not found."""
    pass


class MessageNotSendError(Exception):
    """Occurs when a message was not send to telegram chat."""
    pass
