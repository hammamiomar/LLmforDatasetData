from flask import Flask, render_template, request
from chatManager import MessageManager
from werkzeug.utils import secure_filename
from contextGen import processDataset
import os

import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/upload', methods=['POST'])
def upload():
    user_csv_file = request.files.get("csv_file")
    if user_csv_file and user_csv_file.filename.endswith(".csv"):
        filename = secure_filename(user_csv_file.filename)
        file_path = os.path.join("datasets", filename)
        global message_Manager
        message_Manager = MessageManager(file_path)
        return render_template('index.html')
    else:
        return "Invalid file format"

@app.route('/basic')
def basic():
    message_Manager.genBasic()
    print(message_Manager.get_message_history())
    return message_Manager.get_last_response()

@app.route('/cot')
def cot():
    message_Manager.genCoT()
    print(message_Manager.get_message_history())
    return message_Manager.get_last_response()

@app.route('/discover')
def discover():
    message_Manager.genDiscover()
    print(message_Manager.get_message_history())
    return message_Manager.get_last_response()

@app.route('/zero')
def zero():
    message_Manager.genZero()
    print(message_Manager.get_message_history(zero=True))
    return message_Manager.get_last_response(zero=True)

@app.route('/reset',methods=['POST'])
def reset():
    print("reset")
    message_Manager.reset_message_history()
    return render_template('index.html')
if __name__ == '__main__':
    app.run(port=8000, debug=True)
