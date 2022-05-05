import json

import pytest

from helpers.classes import Question, Questionnaire, ResultManager
from helpers import exceptions


class TestQuestion:
    def test_answer_question(self):
        text = "Are you thirsty?"
        question = Question(text)
        assert question.name == text
        assert question.answered is False
        question.answer_question(True)
        assert question.answered is True

    def test_question_invalid_input(self):
        with pytest.raises(exceptions.InvalidQuestion):
            Question(10)

    @pytest.mark.parametrize(
        "answer",
        [
            1,
            "hello",
            {"a": 1},
            1.1
        ]
    )
    def test_invalid_answer(
            self,
            answer
    ):
        question = Question("Are you hungry?")
        with pytest.raises(exceptions.InvalidAnswer):
            question.answer_question(answer)

    def test_already_answered(
            self
    ):
        question = Question("Are you thirsty?")
        question.answer_question(True)
        with pytest.raises(exceptions.AlreadyAnswered):
            question.answer_question(False)


@pytest.fixture(name="example_questionnaire")
def example_questionnaire():
    return Questionnaire(
        [
            Question("Are you vegan?"),
            Question("Do you eat chocolate though?")
        ]
    )

class TestQuestionnaire:
    def test_length(
            self,
            example_questionnaire
    ):
        assert example_questionnaire.length == 2

    def test_completed(
            self,
            example_questionnaire
    ):
        assert example_questionnaire.completed is False
        example_questionnaire.questions[0].answer_question(True)
        assert example_questionnaire.completed is False
        example_questionnaire.questions[1].answer_question(False)
        assert example_questionnaire.completed is True

    def test_score_incomplete(
            self,
            example_questionnaire
    ):
        with pytest.raises(exceptions.QuestionnaireIncomplete):
            example_questionnaire.calculate_score()

    def test_score_complete(
            self,
            example_questionnaire
    ):
        for question in example_questionnaire.questions:
            question.answer_question(True)
        assert example_questionnaire.calculate_score() == 100.0


@pytest.fixture(name="temp_file_path")
def temp_file_path(tmpdir):
    return tmpdir.join("tempfile.json")


@pytest.fixture(name="demo_data")
def demo_data(temp_file_path):
    with open(temp_file_path) as temp_file:
        json.dump({"results": []}, temp_file)


class TestResultManager:
    @pytest.mark.parametrize(
        "input_data",
        [
            {
                "results": [1.1, 2.2, 3.3]
            },
            {
                "results": []
            }
        ]
    )
    def test_validate_data_valid(
            self,
            input_data
    ):
        result = ResultManager._validate_data_format(input_data)
        assert result

    @pytest.mark.parametrize(
        "input_data",
        [
            {"results": 1},
            {"not_results": [1.1, 2.2]},
            {"results": [1.1, 2.2, 3.3], "something_else": [1.1, 2.2, 3.3]},
            {"results": ["hello", 1.1]},
            {"results": [True, 1.1]},
        ]
    )
    def test_validate_data_invalid(
            self,
            input_data
    ):
        result = ResultManager._validate_data_format(input_data)
        assert not result


    def test_load_results_no_results_file(
            self,
            temp_file_path
    ):
        result_manager = ResultManager(temp_file_path)
        assert result_manager._get_results() == []

    def test_load_results_empty_results_file(
            self,
            temp_file_path
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": []}, temp_file)
        result_manager = ResultManager(temp_file_path)
        assert result_manager._get_results() == []

    def test_load_results_populated_file(
            self,
            temp_file_path
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": [10.0, 20.0, 30.0]}, temp_file)
        result_manager = ResultManager(temp_file_path)
        assert result_manager._get_results() == [10.0, 20.0, 30.0]

    def test_save_result_no_results_file(
            self,
            temp_file_path
    ):
        result_manager = ResultManager(temp_file_path)
        result_manager.save_result(50.0)
        with open(temp_file_path, "r") as temp_file:
            result = json.load(temp_file).get("results")
        assert result == [50.0]

    def test_save_result_with_valid_results_file(
            self,
            temp_file_path,
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": [50.0]}, temp_file)
        result_manager = ResultManager(temp_file_path)
        result_manager.save_result(50.0)
        with open(temp_file_path, "r") as temp_file:
            result = json.load(temp_file).get("results")
        assert result == [50.0, 50.0]

    def test_save_result_invalid_type(
            self,
            temp_file_path,
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": [50.0]}, temp_file)
        result_manager = ResultManager(temp_file_path)
        with pytest.raises(exceptions.InvalidDataFormat):
            result_manager.save_result(True)

    def test_save_result_with_invalid_results_file(
            self,
            temp_file_path
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": [1]}, temp_file)
        result_manager = ResultManager(temp_file_path)
        with pytest.raises(exceptions.InvalidDataFormat):
            result_manager.save_result(50.0)

    def test_get_average_no_results(
            self,
            temp_file_path
    ):
        result_manager = ResultManager(temp_file_path)
        result = result_manager.get_previous_result_stats()
        assert result == {
            "average": 0,
            "count": 0
        }

    def test_get_average_everyone_scored_zero(
            self,
            temp_file_path
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": [0.0, 0.0, 0.0]}, temp_file)
        result_manager = ResultManager(temp_file_path)
        result = result_manager.get_previous_result_stats()
        assert result == {
            "average": 0,
            "count": 3
        }

    def test_get_average(
            self,
            temp_file_path
    ):
        with open(temp_file_path, "w") as temp_file:
            json.dump({"results": [30.0, 20.0, 10.0]}, temp_file)
        result_manager = ResultManager(temp_file_path)
        result = result_manager.get_previous_result_stats()
        assert result == {
            "average": 20.0,
            "count": 3
        }
