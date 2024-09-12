import sqlite3

def create_table():
    connect = sqlite3.connect("user_acc.db")
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account(
            email VARCHAR(256),
            password VARCHAR(256)
        );
    ''')
    connect.commit()
    connect.close()
    
def insert_table(email_input, password_input):
    connect = sqlite3.connect("user_acc.db")
    cursor = connect.cursor()
    cursor.execute(
         """
         INSERT INTO account (email,password)
         VALUES (?,?)
         """,
         (email_input,password_input)
    ) 
    connect.commit()
    connect.close()
    
if __name__ == "__main__":
    create_table()
    