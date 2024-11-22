import random
import json

class Question:
    def __init__(self, section, question_score=20):
        self.section = section
        self.question_score = question_score  # Set default score for each question
        self.questions = self.load_questions()
        self.randomized_questions = self.randomize_questions()  # Shuffle questions
        self.current_question_index = 0  # Start with the first question

    def load_questions(self):
        try:
            with open(f'data/questions/questions_section{self.section}.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: 'data/questions/questions_section{self.section}.json' not found!")
            return []

    def randomize_questions(self):
        """Shuffle questions for randomization."""
        randomized_questions = self.questions[:]
        random.shuffle(randomized_questions)
        return randomized_questions

    def ask_question(self):
        if self.current_question_index >= len(self.randomized_questions):
            print("All questions in this section have been asked.")
            return 0

        selected_question = self.randomized_questions[self.current_question_index]
        self.current_question_index += 1
        print(f"Question: {selected_question['question_text']}")

        options_mapping = {}
        if selected_question['type'] == 'True-False':
            options_mapping = {"1": "True", "2": "False"}
        else:
            options_mapping = {str(idx): option for idx, option in enumerate(selected_question['options'], 1)}

        for idx, option in options_mapping.items():
            print(f"{idx}. {option}")

        user_answer = input("Your answer(s) (You can use numbers or text): ").strip()
        correct_answer = self.get_correct_answer(selected_question)

        if selected_question['type'] in ['True-False', 'Single-Choice']:
            return self.handle_single_choice_or_true_false(selected_question, user_answer, correct_answer, options_mapping)
        else:
            return self.handle_multiple_choice(selected_question, user_answer, correct_answer, options_mapping)

    def handle_single_choice_or_true_false(self, question, user_answer, correct_answer, options_mapping):
        user_answer_normalized = options_mapping.get(user_answer.strip(), user_answer).lower()
        correct_answer_normalized = correct_answer.lower()

        if user_answer_normalized == correct_answer_normalized:
            print("Correct!")
            return self.question_score
        else:
            print(f"Wrong! The correct answer is: {correct_answer}")
            return 0

    def handle_multiple_choice(self, question, user_answer, correct_answer, options_mapping):
        user_answer_set = set(
            options_mapping.get(ans.strip(), ans.strip()).lower() 
            for ans in user_answer.split(',')
        )
        correct_answer_set = set(ans.lower() for ans in correct_answer)

        total_correct_answers = len(correct_answer_set)
        score_per_answer = self.question_score / total_correct_answers if total_correct_answers else 0

        user_score = 0
        for answer in user_answer_set:
            if answer in correct_answer_set:
                user_score += score_per_answer

        user_score = round(user_score, 2)
        print(f"Your score for this question: {user_score}")
        return user_score

    def get_correct_answer(self, question):
        try:
            with open('data/answers/answers.json', 'r') as f:
                answers = json.load(f)
                return answers.get(str(question['id']), "")
        except FileNotFoundError:
            print("Error: 'data/answers/answers.json' file not found.")
            return ""
