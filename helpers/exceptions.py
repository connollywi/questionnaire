class InvalidQuestion(Exception):
    """
    Raised when question created with invalid input
    """


class InvalidAnswer(Exception):
    """
    Raised when question is answered with invalid input
    """


class AlreadyAnswered(Exception):
    """
    Raised when attempting to answer an already answered question
    """


class QuestionnaireIncomplete(Exception):
    """
    Raised when trying to do somethingthat requires a questionnaire to be incomplete
    """


class InvalidDataFormat(Exception):
    """
    Raised when data is not in expected format
    """