import os
from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from pandas import DataFrame
from json import loads
from threading import Thread
from time import sleep

app = Flask(__name__)
app.secret_key = b'nly:6LejsYJEH'

APP_DIR = os.getcwd()
MONGO_CLIENT = MongoClient("mongodb+srv://readonly:6LejsYJEHZDe5qZF@cluster0-6iwz3.mongodb.net/british-quiz-bot?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")
MONGO_DB = MONGO_CLIENT['british-quiz-bot']
DATA_FILE = os.path.join(APP_DIR, 'static', 'data.json')
REPORT_GENERATION_INTERVAL = 600


def get_tests_data():
    query = MONGO_DB.tests.find({}, { 
        'questions.answer': True,
        'questions.question': True,
        'questions.answeredCorrectly': True
    })

    rows = list(map( lambda x: dict(test_id=x['_id'], questions=x['questions']) , query ))
    questions = []
    
    for row in rows:
        for question in row['questions']:
            question['test_id'] = row['test_id']
            questions.append(question)

    return questions


def get_questions_data():
    query = MONGO_DB.questions.find({}, {
        'fields.question_text': True,
        'airtable_id': True,
        'fields.A': True,
        'fields.B': True,
        'fields.C': True,
        'fields.D': True
    })

    rows = list(map( lambda x: dict(id=x['_id'], airtable_id=x['airtable_id'], **x['fields']) , query ))
    return rows


def count_answers(tests, question_id):

    c = {
        'chose_a' : 0,
        'chose_b' : 0,
        'chose_c' : 0,
        'chose_d' : 0,
    }

    for test in tests:
        if test['question'] == question_id:
            if 'A' in test['answer']:
                c['chose_a'] += 1
            elif 'B' in test['answer']:
                c['chose_b'] += 1
            elif 'C' in test['answer']:
                c['chose_c'] += 1
            elif 'D' in test['answer']:
                c['chose_d'] += 1
            
    return c


def prepare_data(questions, tests):

    for question in questions:
        counts = count_answers(tests, question['id'])
        question.update(counts)

    df_tests = DataFrame(tests)
    df_questions = DataFrame(questions)

    df_questions.set_index('id', inplace=True)
    df_tests.answer = df_tests.answer.map(lambda x: ','.join(x))   
    df_tests.drop_duplicates(subset=['test_id', 'question'], inplace=True)

    cols = ['question', 'test_id', 'answeredCorrectly']
    s_correct = df_tests[df_tests.answeredCorrectly == 'true'].groupby(cols).count().groupby('question').sum()
    s_wrong = df_tests[df_tests.answeredCorrectly == 'false'].groupby(cols).count().groupby('question').sum()
    df_questions = df_questions.join(s_correct).fillna(0)
    df_questions.rename(columns={'answer' : 'correct'}, inplace=True)
    df_questions = df_questions.join(s_wrong).fillna(0)
    df_questions.rename(columns={'answer' : 'wrong'}, inplace=True)

    df_questions['attemps'] = df_questions['correct'] + df_questions['wrong']
    df_questions['percent_correct'] = df_questions['correct'] / df_questions['attemps']
    df_questions['percent_correct'] = df_questions['percent_correct'].round(2).fillna(0)
    return df_questions


def generate_questions_report():

    while True:
        # retrieve records from MONGO_DB
        questions = get_questions_data()
        tests = get_tests_data()

        # perform calculations
        df_questions = prepare_data(questions, tests)
        # export to json string
        json = df_questions.to_json(orient='records')
        # write file
        with open(DATA_FILE, 'w') as f: f.write(json)
        # wait to next loop
        sleep(REPORT_GENERATION_INTERVAL)


@app.route('/questions')
def questions():
    # read data file content
    with open(DATA_FILE) as f: content = loads(f.read())
    # return json response
    return jsonify(content)


@app.route('/')
def index():
    return render_template('index.html')

# generate questions report periodically
thread = Thread(target=generate_questions_report)
thread.start()
