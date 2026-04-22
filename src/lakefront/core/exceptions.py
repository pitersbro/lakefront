class LakefrontError(Exception):
    """Base class for all Lakefront exceptions."""


class ProjectNotFoundError(LakefrontError): ...


class ProjectExistsError(LakefrontError): ...


class SourceNotFoundError(LakefrontError): ...


class SourceExistsError(LakefrontError): ...


class SourceTypeInvalidError(LakefrontError): ...


class LlmError(LakefrontError): ...
