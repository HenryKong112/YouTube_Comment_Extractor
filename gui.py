import tkinter as tk
from tkinter import messagebox
import hashlib
import sqlite3
import re
import user_database as udb  # Ensure this module has the 'insert_table' function
import pandas as pd
import googleapiclient.discovery

udb.create_table()

# Define functions
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_password(password):
    return 8 <= len(password) <= 16

def check_login():
    # Get email and password from Entry widgets
    email = email_entry.get().strip()
    password = pw_entry.get()

    # Validate email and password
    if not is_valid_email(email):
        messagebox.showerror("Error", "Please enter a valid email.")
        return
    
    if not is_valid_password(password):
        messagebox.showerror("Error", "Please enter a valid password. (8-16 characters)")
        return

    # Hash the password
    password_encoded = password.encode('utf-8')
    hashed_pw = hashlib.sha256(password_encoded).hexdigest()

    # Connect to the database
    try:
        connect = sqlite3.connect("user_acc.db")
        cursor = connect.cursor()

        # Execute the query with parameterized inputs
        cursor.execute('SELECT * FROM account WHERE email = ? AND password = ?', (email, hashed_pw))
        result = cursor.fetchone()

        # Check query result
        if result is None:
            messagebox.showerror("Error", "Account doesn't exist. Please register an account.")
        else:
            messagebox.showinfo("Login Success", "Login successfully!")
            root.destroy()
            YCE()
                      
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        connect.close()

def check_register():
    # Get email and password from Entry widgets
    email = email_entry.get().strip()
    password = pw_entry.get()

    # Validate email and password
    if not is_valid_email(email):
        messagebox.showerror("Error", "Please enter a valid email.")
        return
    
    if not is_valid_password(password):
        messagebox.showerror("Error", "Please enter a valid password.")
        return

    # Hash the password
    password_encoded = password.encode('utf-8')
    hashed_pw = hashlib.sha256(password_encoded).hexdigest()

    # Connect to the database
    try:
        connect = sqlite3.connect("user_acc.db")
        cursor = connect.cursor()

        # Check if email already exists
        cursor.execute('SELECT * FROM account WHERE email = ?', (email,))
        result = cursor.fetchone()

        if result is not None:
            messagebox.showerror("Error", "Email already exists. Please register using another email.")
        else:
            # Insert new user into the database
            udb.insert_table(email, hashed_pw)
            messagebox.showinfo("Register Success", "Register successfully! You can login now.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        connect.close()

def YCE():
    
    YCE_window = tk.Tk()
    YCE_window.geometry('300x350')
    YCE_window.title('YouTube Comment Extractor')
    # Label
    key_label = tk.Label(YCE_window, text="YouTube API Key : ")
    video_label = tk.Label(YCE_window, text="YouTube Video ID : ")
    # Entry
    key_entry = tk.Entry(YCE_window)
    video_entry = tk.Entry(YCE_window)
    def comment_get(format='excel'):
        try:
            DEVELOPER_KEY = key_entry.get()
            VIDEO_ID = video_entry.get()
            API_SERVICE_NAME = "youtube"
            API_VERSION = "v3"
            youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)
            def get_replies(parent_id):  # Added video_id as an argument
                replies = []
                next_page_token = None
                while True:
                    reply_request = youtube.comments().list(
                        part="snippet",
                        parentId=parent_id,
                        textFormat="plainText",
                        maxResults=100,
                        pageToken=next_page_token
                    )
                    reply_response = reply_request.execute()
                    for item in reply_response['items']:
                        comment = item['snippet']
                        replies.append([
                            comment['authorDisplayName'],
                            comment['parentId'],
                            comment['publishedAt'],
                            comment['likeCount'],
                            comment['textDisplay'],
                            item['id']
                        ])
                    next_page_token = reply_response.get('nextPageToken')
                    if not next_page_token:
                        break
                return replies
            def fetch_comments(video_id):
                comments_list = []
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100
                )
                response = request.execute()
                while True:
                    for item in response['items']:
                        comment = item['snippet']['topLevelComment']['snippet']
                        comments_list.append([
                            comment['authorDisplayName'],
                            item['id'],
                            comment['publishedAt'],
                            comment['likeCount'],
                            comment['textDisplay'],
                        ])
                    try:
                        next_page_token = response['nextPageToken']
                    except KeyError:
                        break
                    request = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100,
                        pageToken=next_page_token
                    )
                    response = request.execute()
                return comments_list

            # Fetch comments for a specific video
            comments = fetch_comments(VIDEO_ID)
            # Get top comments
            df_top_comment = pd.DataFrame(comments,columns=['Username','Comment_ID', 'PublishedAt', 'Like', 'Comment'])
            # Get reply comments
            id_list = df_top_comment["Comment_ID"].to_list()
            reply_list=[]
            for id in id_list:
                reply_get = get_replies(id)
                for i in range(len(reply_get)):
                    one_reply = reply_get[i]
                    reply_list.append(one_reply)
            df_reply = pd.DataFrame(reply_list,columns=['Username','Parent_ID', 'PublishedAt', 'Like', 'Comment','Comment_ID'])
            # Combine 2 dataframes to get all comments
            df_combined = pd.concat([df_top_comment, df_reply], ignore_index=True)
            if format == 'csv':
                df_combined.to_csv(f'{VIDEO_ID}.csv', index=False, header=True)
                messagebox.showinfo('Success', "The CSV file is created successfully.")
            else:
                df_combined.to_excel(f'{VIDEO_ID}.xlsx', index=False, header=True)
                messagebox.showinfo('Success', "The Excel file is created successfully.")
        
        except Exception:
            messagebox.showerror("Error", "Check your API key and video ID again.")
            
    #button
    get_excel_btn = tk.Button(YCE_window, text='Download Excel file',command=lambda: comment_get('excel'))
    get_csv_btn = tk.Button(YCE_window, text='Download CSV file',command=lambda: comment_get('csv'))
    # Layout
    key_label.grid(row=0, column=0, pady=20)
    video_label.grid(row=1, column=0)
    key_entry.grid(row=0, column=1, columnspan=2)
    video_entry.grid(row=1, column=1,columnspan=2)
    get_excel_btn.grid(row=2, column=1,pady = 20)
    get_csv_btn.grid(row=3, column=1,pady = 20)

    YCE_window.mainloop()

# Tkinter setup
root = tk.Tk()
root.geometry('300x350')
root.title('Login')

# Create UI elements
login_label = tk.Label(root, text="Login")
email_label = tk.Label(root, text="Email: ")
pw_label = tk.Label(root, text="Password: ")

email_entry = tk.Entry(root)
pw_entry = tk.Entry(root, show='*')

login_btn = tk.Button(root, text='Login', command=check_login)
register_btn = tk.Button(root, text='Register', command=check_register)

# Layout
login_label.grid(row=0, column=1, columnspan=2, pady=20)
email_label.grid(row=1, column=0, padx=30)
pw_label.grid(row=2, column=0)
email_entry.grid(row=1, column=1, columnspan=2)
pw_entry.grid(row=2, column=1, columnspan=2)
login_btn.grid(row=3, column=1)
register_btn.grid(row=3, column=2)

root.mainloop()
