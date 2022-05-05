# Questionnaire 
A simple CLI based questionnaire app which asks questions based on an input file, 
calculates a score, stores the result and displays previous results.

The main questionnaire functionality is implemented using several classes, which are then 
utilised in a simple CLI script.

Data is stored and managed locally in a JSON file.


#Questionnaire Questions
Questions are stored in a simple text file in "/questions.txt". They should be organised 
in the following format with each new question on its own line:

    Question Name
    ---------------------------
    Question one?
    Question two?
    
The first two lines will be disregarded.


# Setup/Installation
I'd recommend using a virtual environment with at least Python 3.6 when running the 
questionnaire:
- create a new python3 virtual environment `python3 -m venv {environment_name}`
- activate the virtual environment `source {environment_name}/bin/activate`
- install the required packages `pip install -r requirements.txt`


#Running tests
Tests for the classes/main functionality have been written using pytest. Tests can 
be run by entering the command `pytest` in your activated virtual environment.


#Running the Questionnaire
To run the questionnaire, run the questionnaire_cli.py script 
`python questionnaire_cli.py`


#Resetting Data
You can reset the locally stored data by using the --reset argument: 
`python questionnaire_cli.py --reset`


#Data Integrity
The questionnaire app will check and maintain the integrity of the locally stored 
data. If the file is altered in a way that will prevent the result  manager from 
loading from or saving to it, the data will be reset to its initial empty state.


# Potential Future Improvements/Thoughts
- Handle more than one set of questions/questionnaires, with method of selecting.
- Implement a more robust method of persisting data, such as SQLAlchemy and a
  database.
- More robust data integrity/validation. Of course a user could edit the 
  results.json file and add a new result. However implementing this seems a little 
  OTT for such a rudimentary method of persisting data that only exists for a 
  demo/challenge and would not be used in production.
- Questionnaire classes could be hooked into a nicer front end/interface with some
  tweaks.
- Versioning of questionnaires/detect changes to input questions. Currently
  questions can be updated with no way of separating data related to one set 
  of questions from another.
