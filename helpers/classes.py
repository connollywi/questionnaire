"""Classes which can be used to manage questionnaires"""

import json
from typing import List

from .exceptions import *


class Question:
    """
    Class representing a question

    Questions have a name (ie the actual text of the question) and hopefully will have
    an answer at some point. Questions may be answered as True (yes) or False (no). Once
    a question has been answered the question cannot be answered again. The answered
    status can be found via the answered property.

    Parameters
    ----------
    name
        The name/text of the question.

    Attributes
    ----------
    name
        The name/text of the question.
    answer
        The answer to the question.

    """
    answer = None

    def __init__(
            self,
            name: str
    ):
        if not isinstance(name, str):
            raise InvalidQuestion
        self.name = name

    def answer_question(
            self,
            answer: bool
    ):
        """
        Sets the answer for a question instance.

        Parameters
        ----------
        answer
            A boolean representing if the answer is a Yes(True) or No(False).

        Attributes
        ----------
        answer
            A boolean representing if the answer is a Yes(True) or No(False).


        Raises
        ----------
        InvalidAnswer
            Raised if the provided answer is not boolean.
        AlreadyAnswered
            Raised when attempting to answer an already answered question.

        """
        if not isinstance(answer, bool):
            raise InvalidAnswer
        if not self.answer:
            self.answer = answer
        else:
            raise AlreadyAnswered

    @property
    def answered(self):
        """
        Whether or not the question has been answered, True for answered, False
        for not answered.
        """
        return self.answer is not None


class Questionnaire:
    """
    Class representing a questionnaire.

    Questionnaires contain a list of questions. The length of the questionnaire
    is amount of questions within the questionnaire. QWhen completed, the score
    can be determined. Questionnaires are completed when every question has
    been answered.

    Parameters
    ----------
    questions
        A list of Question objects.

    Attributes
    ----------
    questions
        A list of Question objects.

    """
    def __init__(
            self,
            questions: List[Question]
    ):
        self.questions = questions

    def calculate_score(
            self
    ) -> float:
        """
        Calculates the score for the questionnaire instance.


        Score is calculated by getting the percentage (rounded to two places) of
        questions with a yes answer out of the total amount of questions in the
        questionnaire. The score can only be calculated if the questionnaire
        has been completed (all questions answered).

        Returns
        -------
        float
            The calculated score

        Raises
        -------
        QuestionnaireIncomplete
            raised if score calculation is attempted on an incomplete questionnaire.

        """
        if not self.completed:
            raise QuestionnaireIncomplete
        answered_yes = list(filter(lambda x: x.answer is True, self.questions))
        return (len(answered_yes)/self.length) * 100

    @property
    def completed(
            self
    ) -> bool:
        """
        Whether the questionnaire has been completed (all questions answered).
        """
        return all(question.answered for question in self.questions)

    @property
    def length(
            self
    ) -> int:
        """
        The questionnaire length (amount of questions).
        """
        return len(self.questions)


class ResultManager:
    """
    Class responsible for results loading/saving and providing insights on past results.

    Reads and writes data from/to a JSON file, which will be created if not already present.
    Data integrity is validated before reads and writes, and if errors are found, an
    InvalidData exception will be raised. Data can also be reset back to the empty state.

    Parameters
    ----------
    results_path
        The path to the file where results are to be stored.

    Attributes
    ----------
    results_path
        The path to the file where results are to be stored.

    """
    def __init__(
            self,
            results_path: str
    ):
        self.results_path = results_path

    @staticmethod
    def _validate_data_format(
            data
    ) -> bool:
        """
        Checks that data is in the correct format (a dictionary with one key "results"
        which contains a list of floats).

        Parameters
        ----------
        data
            The data to be validated.

        Returns
        -------
        Bool
            True if data is valid, otherwise False.
        """
        if isinstance(data, dict):
            if list(data.keys()) == ["results"]:
                if isinstance(data["results"], list):
                    return all(isinstance(entry, float) for entry in data.get("results"))
        return False

    def reset_file(self):
        with open(self.results_path, "w") as results_file:
            json.dump({"results": []}, results_file, indent=4)

    def _read_file(
            self
    ) -> dict:
        """
        Reads in data from the instance results path

        Returns
        -------
        results
            A dictionary of the results

        """
        try:
            with open(self.results_path, "r") as results_file:
                results = json.load(results_file)
        except FileNotFoundError:
            results = {"results": []}
        return results

    def _write_file(
            self,
            data: dict
    ):
        """
        Writes data to file
        Parameters
        ----------
        data
            data to be saved

        """
        with open(self.results_path, "w") as results_file:
            json.dump(data, results_file, indent=4)

    def _get_results(self):
        """
        Gets results from data file
        Returns
        -------
        list[float]
            A list of previous results

        """
        data = self._read_file()
        if self._validate_data_format(data):
            return data["results"]
        else:
            raise InvalidDataFormat

    def get_previous_result_stats(
            self
    ) -> dict:
        """
        Gets previous results stats

        Returns
        -------

        """
        results = self._get_results()
        if len(results) == 0:
            average = 0
        else:
            average = sum(results)/len(results)
        return {
            "average": round(average, 2),
            "count": len(results)
        }

    def save_result(
            self,
            result: float
    ):
        """
        Saves a result to file

        Parameters
        ----------
        result
            The result (a float) to be saved

        """
        if not isinstance(result, float):
            raise InvalidDataFormat
        else:
            results = self._get_results()
            results.append(result)
            self._write_file({"results": results})
