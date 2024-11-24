import json
import hashlib
import os


def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.strip().encode('utf-8')).hexdigest()


class User:
    def __init__(self, username, surname, student_number=None, teacher_id=None, password=None, role=None):
        self.username = username
        self.surname = surname
        self.password = hash_password(password) if password else None
        self.student_number = student_number
        self.teacher_id = teacher_id
        self.role = role
        self.attempts = 0
        self.score = 0
        self.max_attempts = 2
        self.success_per_section = {"section1": 0, "section2": 0, "section3": 0, "section4": 0}

    def load_user_data(self):
        try:
            with open("user/users.json", "r") as f:
                users_data = json.load(f)

            if self.username in users_data:
                user_data = users_data[self.username]
                # self.username = users_data['username'] 
                self.password = user_data['password']  # Load the hashed password
                self.surname = user_data['surname']
                self.attempts = user_data['attempts']
                self.score = user_data['score']
                self.success_per_section = user_data['success_per_section']
                self.student_number = user_data['student_number']
                self.teacher_id = user_data.get('teacher_id')
                self.role = user_data.get('role')  # Load role if available
            else:
                print(f"User '{self.username}' not found in the database. Adding user...")
                self.save_user_data(users_data)

        except FileNotFoundError:
            print("users/users.json file not found. Creating a new one.")
            self.save_user_data()
        except json.JSONDecodeError:
            print("The users.json file is empty or corrupted. Creating a new one.")
            self.save_user_data()

    def save_user_data(self, users_data=None):
        if users_data is None:
            try:
                with open("user/users.json", "r") as f:
                    users_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                users_data = {}

        # Use student_number or teacher_id as the unique key
        unique_id = self.student_number if self.student_number else self.teacher_id

        # Determine the role and save the appropriate fields
        if self.teacher_id:  # Teacher
            users_data[unique_id] = {
                "username": self.username,
                "surname": self.surname,
                "teacher_id": self.teacher_id,
                "password": self.password,  # Save the hashed password
                "role": self.role  # Teacher's subject
            }
        elif self.student_number:  # Student
            users_data[unique_id] = {
                "username": self.username,
                "surname": self.surname,
                "student_number": self.student_number,
                "password": self.password,  # Save the hashed password
                "attempts": self.attempts,
                "score": round(self.score, 2),
                "success_per_section": {
                    k: round(v, 2) for k, v in self.success_per_section.items()
                }
            }

        with open("user/users.json", "w") as f:
            json.dump(users_data, f, indent=4)

    def has_attempts_left(self):
        return self.attempts < self.max_attempts

    def increment_attempts(self):
        self.attempts += 1

    def update_score(self, section, correct_answers, total_questions):
        section_score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0
        self.success_per_section[section] = section_score
        self.calculate_overall_score()

    def calculate_overall_score(self):
        total_score = sum(self.success_per_section.values())
        self.score = round(total_score / len(self.success_per_section), 2)

    def get_score(self):
        return round(self.score, 2)
