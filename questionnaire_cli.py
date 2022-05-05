"""Simple script to run a basic Y/N questionnaire as a CLI app and store results"""
import sys
import time
from distutils.util import strtobool
from os import name, system
from helpers.classes import Question, Questionnaire, ResultManager
from helpers import exceptions


def get_questions(path):
    """
    Opens and parses txt files to get question names. Files should be of
    the format:

        Question Name
        ---------------------------
        Question 1?
        Question 2?

    The first two lines will be disregarded.

    Returns
    -------
    List
        List of question names.
    """
    with open(path, "r") as input_file:
        data = [line.strip('\n') for line in input_file][2:]
    return data


def clear():
    """
    Clears the terminal screen
    """
    system("cls") if name == "nt" else system("clear")


def display_question_get_input(
        question
) -> bool:
    """
    Displays a question and captures the user input for that question.

    Answers must be Y or N, returning True or False respectively. User
    input is validated, and incorrect inputs will display a prompts to
    the user to only enter Y or N and allowing them to re-answer.

    Parameters
    ----------
    question
        The question to be displayed and answered by users
    Returns
    -------
    bool
        True if user input was "Y", false if "N".
    """
    clear()
    sys.stdout.write(question + " (Y/N): ")
    while True:
        try:
            return bool(strtobool(input().lower()))
        except ValueError:
            print("Invalid input! Please only enter Y or N.")


def display_messages(
        count: int,
        messages: list
):
    """
    Briefly displays messages.

    Messages are displayed for a set period of time. Display time is determined by
    the count value, with each count representing one second. A visible countdown
    of remaining time in seconds is displayed to the user.

    """
    while count > 0:
        clear()
        for message in messages:
            print(message)
        print(f"{count}")
        time.sleep(1)
        count -= 1


def display_results(
        score: float,
        previous_results_data: dict
):
    """
    Displays information about the user score and previous scores.

    Each time a questionnaire is taken, the results are stored locally.
    From these results, the average score of all previous results is
    determined. This along with the amount of previous results is displayed
    alongside the user score.

    The total average does not include the user's score, which is added to
    the results afterward. If no questionnaires have been recorded yet this
    additional information is replaced with a message to the user that there
    are no previous entries/attempts recorded.

    Parameters
    ----------
    score
        The score to display
    previous_results_data
        Information about previous results (total average and amount of results)

    """
    print(f"Your result: {score}")
    if previous_results_data["count"] == 0:
        print("You are the first to take this questionnaire")
        print("There are no previous results")
    else:
        print(f"The average result so far (not including yours) is: {previous_results_data['average']}")
        print(f"Total previous results: {previous_results_data['count']}")


def confirm_reset_data(
        result_manager: ResultManager
):
    """
    Confirms whether the user wishes to reset data, and if so...does (then exits)!

    Parameters
    ----------
    result_manager
        An instance of a ResultManager object for managing data reads/writes and
        integrity

    """
    prompt = display_question_get_input("Are you sure you want to reset/delete stored data?")
    if prompt:
        result_manager.reset_file()
        display_messages(
            5,
            [
                "Data has been reset/deleted!",
                "Closing in:"
            ]
        )
    else:
        display_messages(
            5,
            [
                "Data has NOT been reset/deleted!",
                "Closing in:"
            ]
        )
    clear()
    sys.exit()


def get_previous_result_stats(
        result_manager: ResultManager
) -> dict:
    """
    Retrieves previous result information from a ResultManager.

    If the data has been corrupted, it will be reset with a message displayed.

    Parameters
    ----------
    result_manager
        An instance of a ResultManager object for managing data reads/writes and
        integrity.

    Returns
    -------
    dict
        Information about previous results (total average and amount of stored results).

    """
    try:
        previous_results_data = result_manager.get_previous_result_stats()
    except exceptions.InvalidDataFormat:
        result_manager.reset_file()
        previous_results_data = result_manager.get_previous_result_stats()
        display_messages(
            5,
            [
                "Result data was corrupted and had to be deleted/reset",
                "Continuing in:"
            ]
        )
    return previous_results_data


def save_result(
        result: float,
        result_manager: ResultManager
):
    """
    Saves a result via the passed in ResultManager instance.

    If the data has been corrupted, it will be reset with a message displayed.

    Parameters
    ----------
    result
        The result to save
    result_manager
        An instance of a ResultManager object for managing data reads/writes and
        integrity.

    """
    try:
        result_manager.save_result(result)
    except exceptions.InvalidDataFormat:
        result_manager.reset_file()
        save_result(
            result,
            result_manager
        )
        display_messages(
            5,
            [
                """Data was corrupted and had to be deleted and replaced.""",
                f"""Your result of {result} has been saved to the newly created data.""",
                """Closing in:"""
            ]
        )
        clear()
        sys.exit()


def run_questionnaire(
        questionnaire: Questionnaire,
        result_manager: ResultManager
):
    """
    Runs a questionnaire

    Implements simple logic for running a cli implementation of a questionnaire.
    First, an attempt is made to load in previous results, during which the
    validity of the previous results data is checked. If the results data has
    been tampered with in such a way that the results manager cannot manage it,
    the data will have to be reset to an empty initialized state.

    If this is the case, a brief warning message is triggered with the display time
    in seconds provided.

    Parameters
    ----------
    questionnaire
        An instance of a Questionnaire object for running a questionnaire
    result_manager
        An instance of a ResultManager object for managing data reads/writes and
        integrity

    """
    if "--reset" in sys.argv:
        confirm_reset_data(result_manager)

    previous_results_data = get_previous_result_stats(result_manager)

    count = 0
    while not questionnaire.completed:
        for question in questionnaire.questions:
            count += 1
            answer = display_question_get_input(question.name)
            question.answer_question(answer)
    score = questionnaire.calculate_score()
    display_results(score, previous_results_data)
    save_result(score, result_manager)


def main():
    """
    Starts the application logic when the app is run as __main__.

    """
    questions = [Question(question) for question in get_questions("data/questions.txt")]
    questionnaire = Questionnaire(
        questions
    )
    result_manager = ResultManager("results.json")
    run_questionnaire(
        questionnaire,
        result_manager
    )

if __name__ == "__main__":
    main()

