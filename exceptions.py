class MessageNotSendError(Exception):
    """Occurs when a message was not send to telegram chat."""
    pass


class InvalidStatusCode(Exception):
    """Occurs when the response code is not equal to "200"."""
    pass
