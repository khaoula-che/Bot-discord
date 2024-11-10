# config.py
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")
QUIZ_FILE = 'quizzes.json'
FEEDBACK_FILE = 'feedback.json'
USER_DATA_FILE = 'user_data.json'
