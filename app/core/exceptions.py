class JarvisException(Exception):

    def __init__(self,message:str):
        self.message=message
        super().__init__(message)

    def ConfigurationError(JarvisException):
        """Raised when application configuration is invalid"""

    class AgentExecutionError(JarvisException):
    """Raised when agent execution fails."""


    class ToolExecutionError(JarvisException):
    """Raised when a tool execution fails."""


    class LLMProviderError(JarvisException):
    """Raised when an LLM provider fails."""