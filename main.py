import json
from project_tools import *  # Tüm modülleri import eder



def signup():
    print("\n--- Sign Up ---")
    username = input("Choose a username: ").strip()
    surname = input("Enter your surname: ").strip()
    student_number = input("Enter your student number: ").strip()

    while True:
        password = input("Choose a 4-digit password: ").strip()
        if len(password) == 4 and password.isdigit():
            break
        print("Password must be exactly 4 digits.")

    user = User(username, surname, student_number, password)

    try:
        with open("user/users.json", "r") as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users_data = {}

    if username in users_data:
        print("Username already exists. Please choose another.")
        return None
    else:
        user.save_user_data(users_data)
        print(f"User '{username}' successfully registered.")
        return user


def login():
    print("\n--- Login ---")
    username = input("Enter your username: ").strip()

    try:
        with open("user/users.json", "r") as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No users found. Please sign up first.")
        return None

    if username not in users_data:
        print("Username not found. Please sign up first.")
        return None

    user_data = users_data[username]

    user = User(
                username,
                user_data['surname'],
                user_data['student_number'],
                user_data['password']
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
        if hash_password(password) == user_data['password']:
            print("Login successful.")
            return user
        else:
            print("Incorrect password. Try again.")
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