import sqlite3


#ВОПРОСЫ
question_connection = sqlite3.connect('Telegram bots/Quizle/tables/questions.db', check_same_thread=False)
question_cursor = question_connection.cursor()


question_cursor.execute('''CREATE TABLE IF NOT EXISTS Questions (
               
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               question TEXT,
               answer_1 TEXT,
               answer_2 TEXT,
               answer_3 TEXT,
               answer_4 TEXT,
               answer_correct INTEGER
            )''')
question_connection.commit()


def get_all_questions():
    question_cursor.execute("SELECT * FROM Questions")
    return question_cursor.fetchall()


def create_new_questions(questions_data):
    question_cursor.execute('DELETE FROM Questions')

    list_position = 0
    for string in range(5):
        question = questions_data[list_position].split(':')[0]         #a: b, c, d, e; f
        correct_answer = questions_data[list_position].split(';')[1]
        answers = questions_data[list_position].split(';')[0].split(':')[1].split(',')
        list_position += 1

        question_cursor.execute('''INSERT INTO Questions (
                                question, 
                                answer_1, 
                                answer_2, 
                                answer_3, 
                                answer_4, 
                                answer_correct
                                ) 
                                VALUES (
                                        ?,?,?,?,?,?
                                        )''', 
                                [
                                    question, 
                                    answers[0], 
                                    answers[1], 
                                    answers[2], 
                                    answers[3], 
                                    correct_answer
                                ])
    
    question_connection.commit()
#ЮЗЕРЫ
user_connection = sqlite3.connect('Telegram bots/Quizle/tables/users.db', check_same_thread=False)
user_cursor = user_connection.cursor()


user_cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                    
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    score INTEGER,
                    access_level INTEGER
                    )''')

user_connection.commit()


def user_check(username, check):
    user_cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    try:
        result = user_cursor.fetchone()
        if check == 'existance':
            return result
        elif check == 'access_level':
            access_level = result[3]
            return access_level
    except:
        return False

def get_users(type):
    if type == 'top_10':
        user_cursor.execute("SELECT username, score FROM Users ORDER BY score DESC LIMIT 10")
        users = user_cursor.fetchall()
        lederbord_lines = []
        for position in range(10):
            if position < len(users):
                username, score = users[position]
                lederbord_lines.append(f'{position+1}. {username} - {score}')
            else:
                lederbord_lines.append(f'{position+1}. — - —')
        answer_text = '\n'.join(lederbord_lines)
        return answer_text
    
    # elif type == 'all':
    #     user_cursor.execute("SELECT username, access_level FROM Users")
    #     username, access_level = user_cursor.fetchall()[0]
    #     return username, access_level

def add_user(username, score, access_level):
    try:           #Защита от ошибок
        user_cursor.execute('''INSERT OR IGNORE INTO Users (
                            username,
                            score,
                            access_level
                            )
                            VALUES (
                                ?,?,?
                                )''',
                            [
                                username,
                                score,
                                access_level
                            ])
        
        user_connection.commit()

    except Exception as error:
        print(f'Ошибка при добавлении пользователя: {error}')

# def update_user(username, updated_access_level):
#     try:
#         user_cursor.execute('''UPDATE Users SET access_level = ? WHERE username = ?''')
#     except Exception as error:
#         print(f'Ошибка при обновлении пользователя: {error}')
# user_cursor.execute("SELECT * FROM Users WHERE username = ?", ('LoyaLussT',))
# access_level = user_cursor.fetchone()[3]
# print(access_level)

# print(get_top_users())SELECT * FROM my_table ORDER BY column_name ASC

user_cursor.execute("SELECT username, access_level FROM Users")
a = user_cursor.fetchall()
print(a)

# user_cursor.execute('INSERT INTO Users (username, score, access_level) VALUES (?,?,?)', ['Anon1342', 60, 1])
# user_cursor.execute('INSERT INTO Users (username, score, access_level) VALUES (?,?,?)', ['Anon0174', 96, 1])
# user_connection.commit()