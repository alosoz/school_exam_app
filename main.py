from user import User, hash_password
from timer import Timer
from questions import Question
from exam import Exam
import json
import random

def generate_unique_id(users_data, role):
    """
    Generates a unique ID based on the role (student or teacher).
    """
    prefix = "S" if role == "student" else "T"
    while True:
        new_id = f"{prefix}{random.randint(1000, 9999)}"
        # Ensure uniqueness
        if all(user_data.get("student_number") != new_id and user_data.get("teacher_id") != new_id for user_data in users_data.values()):
            return new_id

def signup():
    print("\n--- Sign Up ---")
    username = input("Choose a username: ").strip().lower().capitalize()
    surname = input("Enter your surname: ").strip().lower().capitalize()
    
    while True:
        role = input("Are you signing up as a student or teacher? (student/teacher): ").strip().lower()
        if role in ["student", "teacher"]:
            break
        print("Invalid choice. Please enter 'student' or 'teacher'.")


    # If teacher, ask for their subject from a predefined list
    subject = None
    if role == "teacher":
        subjects = ["Mathematics", "Physics", "Chemistry", "Geography"]
        print("\nAvailable subjects:")
        for i, subj in enumerate(subjects, 1):
            print(f"{i}. {subj}")
        while True:
            try:
                choice = int(input("Enter the number corresponding to the subject you teach: ").strip())
                if 1 <= choice <= len(subjects):
                    subject = subjects[choice - 1]
                    break
                else:
                    print(f"Please select a valid number between 1 and {len(subjects)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    
    while True:
        password = input("Choose a 4-digit password: ").strip()
        if len(password) == 4 and password.isdigit():
            break
        print("Password must be exactly 4 digits.")


    try:
        with open("user/users.json", "r") as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users_data = {}


    # Generate unique ID based on the role
    unique_id = generate_unique_id(users_data, role)

    # Create the user object
    user = User(
        username=username,
        surname=surname,
        student_number=unique_id if role == "student" else None,
        teacher_id=unique_id if role == "teacher" else None,
        password=password,
        role=subject if role == "teacher" else None
    )
    

   
    user.save_user_data(users_data)
    print(f"User '{username}' successfully registered.")
    return user


def login():
    print("\n--- Login ---")
    user_id = input("Enter your Student Number or Teacher ID: ").strip()

    try:
        with open("user/users.json", "r") as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No users found. Please sign up first.")
        return None

    # Find the user by ID
    user_data = None
    for username, data in users_data.items():
        if data.get("student_number") == user_id or data.get("teacher_id") == user_id:
            user_data = data
            break

    if not users_data:
        print("User not found. Please sign up first.")
        return None

    user_data = users_data[username]
    # load_password = users_data[username]['password']


    # Determine the role and ID type
    role = "teacher" if user_data.get("teacher_id") else "student"
    print(f"Welcome {user_data['username']} ({role.capitalize()}).")
    
    # Check if the user has attempts left
    user = User(
        username,
        user_data['username'],
        user_data['surname'],
        user_data.get('student_number'),
        user_data.get('password'),
        user_data.get('teacher_id')
    )
    
    # Check if the user has attempts left
    if not user.has_attempts_left():
        print("You have exceeded the maximum number of login attempts. Please try again later.")
        return None
    
    user.increment_attempts()
    password_try = 0
    while password_try < 3:
        password_try += 1
        password = input("Enter your password: ").strip()
        hashed_input_password = hash_password(password)

        if hashed_input_password == user_data['password']:
            print("Login successful.")
            return user
        else:
            print("Incorrect password. Try again.")
            password_try += 1
    
    print("Too many failed login attempts.")
    return None

def start_exam():
    while True:
        print("\n--- Welcome to the Exam System ---")
        print("1. Login")
        print("2. Sign Up")
        choice = input("Choose an option (1 or 2): ").strip()

        if choice == "1":
            user = login()
        elif choice == "2":
            user = signup()
        else:
            print("Invalid choice. Please try again.")
            continue

        if not user:
            continue


        print(f"Welcome {user.username}! Starting your exam...")

        # Exam setup
        time_limit = 1800  # 30 minutes
        timer = Timer(time_limit)
        timer.start_timer()
        user.increment_attempts()
        
        total_score = 0  # Total score across sections
        exam_finished = False  # Flag to track if exam ends early

        for section in range(1, 5):
            print(f"...........................................................................\n--- Starting Section {section} ---")
            question = Question(section)  # Load questions for the section
            correct_answers = 0
            total_questions = 5  # Assume 5 questions per section

            for _ in range(total_questions):
                if not timer.check_time():
                    print("\nTime's up! Ending the exam.")
                    exam_finished = True
                    break

                # Display remaining time
                remaining_time = timer.get_remaining_time()
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                print(f"Remaining time: {minutes} minutes {seconds} seconds")

                # Ask a question and update score
                score = question.ask_question()
                correct_answers += (score / question.question_score)

            # Update section score
            user.update_score(f"section{section}", correct_answers, total_questions)
            section_score = user.success_per_section[f"section{section}"]
            total_score += section_score

            print(f"Section {section} completed. Correct Answers: {correct_answers}/{total_questions}, Score: {section_score:.2f}/100")
            if section_score < 75:
                break
            if exam_finished:
                break

        # Finalize and save user data
        user.save_user_data()

        # Display overall results
        overall_score = user.get_score()
        print(f"\n--- Exam Completed ---")
        print(f"Your overall success score: {overall_score:.2f}%")

        if overall_score >= 75:
            print("Congratulations! You passed the exam.")
        else:
            print("Unfortunately, you failed the exam. Better luck next time!")

        break


if __name__ == "__main__":
    start_exam()