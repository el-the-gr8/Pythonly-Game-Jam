import mysql.connector 
import random 
 
# DB Setup 
DB_CONFIG = { 
    'host': 'localhost', 
    'user': 'root', 
    'password': '1234', 
    'database': 'quiz_db' 
} 
 
def get_connection(): 
    return mysql.connector.connect(**DB_CONFIG) 
def init_db(): 
    try: 
        conn = get_connection() 
        c = conn.cursor() 
 
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS questions ( 
                id INT AUTO_INCREMENT PRIMARY KEY, 
                subject VARCHAR(50) NOT NULL, 
                question TEXT NOT NULL, 
                answer TEXT NOT NULL 
            ) 
        ''') 
 
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS scores ( 
                username VARCHAR(100), 
                points INT 
            ) 
        ''') 
 
        conn.commit() 
        conn.close() 
    except mysql.connector.Error as err: 
        print(f"Error during DB initialization: {err}") 
 
def seed_questions(): 
    sample_data = { 
        "science": [ 
            ("What planet is known as the Red Planet?", "Mars"), 
            ("What gas do plants absorb from the atmosphere?", "Carbon Dioxide"), 
            ("What is the chemical symbol for water?", "H2O"), 
            ("How many legs does a spider have?", "8"), 
            ("What part of the plant conducts photosynthesis?", "Leaf"), 
        ], 
        "gk": [ 
            ("Who is the current Secretary General of the UN?", "Antonio Guterres"), 
            ("What is the capital of Australia?", "Canberra"), 
            ("Which country gifted the Statue of Liberty to the USA?", "France"), 
            ("What year did World War II end?", "1945"), 
            ("What is the largest continent?", "Asia"), 
        ], 
        "entertainment": [ 
            ("Who directed the movie Inception?", "Christopher Nolan"), 
            ("Which singer is known as the 'Queen of Pop'?", 
"Madonna"), 
            ("What TV show features the character Walter White?", 
"Breaking Bad"), 
            ("What is the name of the wizarding school in Harry Potter?", "Hogwarts"), 
 
            ("Which movie features the song 'Let It Go'?", "Frozen"), 
        ] 
    } 
 
    conn = get_connection() 
    c = conn.cursor() 
    for subject, q_list in sample_data.items(): 
        for q, a in q_list: 
            c.execute("SELECT * FROM questions WHERE question = %s AND subject = %s", (q, subject)) 
            if not c.fetchone(): 
                c.execute("INSERT INTO questions (subject, question, answer) VALUES (%s, %s, %s)", (subject, q, a)) 
    conn.commit() 
    conn.close() 
 
def login(): 
    username = input("Enter your username to login: ").strip() 
    print(f"Welcome, {username}!") 
    return username 
 
def choose_subject(): 
    subjects = ['science', 'gk', 'entertainment'] 
    print("\nChoose a subject:") 
    for i, sub in enumerate(subjects, 1): 
        print(f"{i}. {sub.capitalize()}") 
    while True: 
        try: 
            choice = int(input("Enter choice (1-3): ")) 
            if 1 <= choice <= 3: 
                return subjects[choice - 1] 
        except ValueError: 
            pass 
        print("Invalid choice. Try again.") 
 
def load_questions(subject): 
    conn = get_connection() 
    c = conn.cursor() 
    c.execute("SELECT question, answer FROM questions WHERE subject = %s", (subject,)) 
    all_qs = c.fetchall() 
    conn.close() 
    random.shuffle(all_qs) 
    return all_qs[:5] 
 
def play_quiz(username, subject): 
    questions = load_questions(subject) 
    total_score = 0 
 
    for q_num, (question, answer) in enumerate(questions, 1): 
        print(f"\nQuestion {q_num}: {question}") 
        for attempt in range(3): 
            user_ans = input("Your answer: ").strip() 
            if user_ans.lower() == answer.lower(): 
                score = [10, 5, 2][attempt] 
                print(f"Correct! You earned {score} points.") 
                total_score += score 
                break 
            else: 
                print("Incorrect.") 
                if attempt == 2: 
                    print("Game over! You used all 3 attempts.") 
                    store_score(username, total_score) 
                    return 
                else: 
                    print("Try again.") 
 
    print("\n You completed the quiz!") 
    print(f"Total Score: {total_score}") 
    store_score(username, total_score) 
 
def store_score(username, points): 
    conn = get_connection() 
    c = conn.cursor() 
    c.execute("INSERT INTO scores (username, points) VALUES (%s, %s)", (username, points)) 
    conn.commit() 
    conn.close() 
 
def show_scores(): 
    print("\n Scoreboard:") 
    conn = get_connection() 
    c = conn.cursor() 
    c.execute("SELECT username, points FROM scores ORDER BY points DESC") 
    rows = c.fetchall() 
    conn.close() 
    for i, row in enumerate(rows, 1): 
        print(f"{i}. {row[0]} - {row[1]} points") 
 
def add_question(): 
    print("\n Add your own question") 
    subject = input("Enter subject (science/gk/entertainment): ").strip().lower() 
    if subject not in ['science', 'gk', 'entertainment']: 
        print("Invalid subject.") 
        return 
    question = input("Enter the question: ").strip() 
    answer = input("Enter the answer: ").strip() 
    conn = get_connection() 
    c = conn.cursor() 
    c.execute("INSERT INTO questions (subject, question, answer) VALUES (%s, %s, %s)", (subject, question, answer)) 
    conn.commit() 
    conn.close()  
    print("Question added successfully!") 
 
#  main function 
def main(): 
    init_db() 
    seed_questions() 
    username = login() 
    subject = choose_subject() 
    play_quiz(username, subject) 
    show_scores() 
 
    while True: 
        add_more = input("\nWould you like to add a new question? (yes/no): ").strip().lower() 
        if add_more == "yes": 
            add_question() 
        else: 
            print("Thank you for playing!") 
            break 
 
if __name__ == "__main__": 
    main() 
