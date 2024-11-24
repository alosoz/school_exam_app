import json
import random

class QuestionBank:
    def __init__(self, file_path):
        """
        Initialize the QuestionBank class and load questions from a JSON file.
        
        :param file_path: Path to the JSON file containing questions.
        """
        self.file_path = file_path
        self.questions = self.load_questions()

    def load_questions(self):
        """
        Load questions from the JSON file.

        :return: Dictionary with sections as keys and their respective questions as values.
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {self.file_path}")
            return {}

    def add_question(self, section, question):
        """
        Add a new question to a specific section.

        :param section: The section to which the question belongs.
        :param question: The question to add (a dictionary with keys like "question_text", "options", "correct_answer").
        """
        if section not in self.questions:
            self.questions[section] = []
        self.questions[section].append(question)

    def get_question(self, section, index):
        """
        Retrieve a question from a specific section by index.

        :param section: The section from which to retrieve the question.
        :param index: The index of the question within the section.
        :return: The question as a dictionary, or None if not found.
        """
        if section in self.questions and 0 <= index < len(self.questions[section]):
            return self.questions[section][index]
        return None

    def get_random_questions(self, section, num_questions):
        """
        Retrieve a specified number of random questions from a section.

        :param section: The section from which to retrieve questions.
        :param num_questions: The number of questions to retrieve.
        :return: A list of random questions, or an empty list if the section is invalid or has insufficient questions.
        """
        if section in self.questions:
            return random.sample(self.questions[section], min(num_questions, len(self.questions[section])))
        return []

    def save_questions(self):
        """
        Save the updated questions back to the JSON file.
        """
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.questions, file, indent=4)
        except Exception as e:
            print(f"Error saving questions: {e}")

#
