"""Core OpenVTO functionality."""


class OpenVTO:
    """Main OpenVTO client for virtual try-on generation.

    Example:
        >>> from openvto import OpenVTO
        >>> vto = OpenVTO()
        >>> vto.hello()
        'Hello from OpenVTO!'
    """

    def __init__(self) -> None:
        """Initialize the OpenVTO client."""
        pass

    def hello(self) -> str:
        """Return a greeting message.

        Returns:
            A hello world string.
        """
        return "Hello from OpenVTO!"

