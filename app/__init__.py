from flask import Flask, render_template, jsonify, Response
from pymongo import MongoClient
from bson.json_util import dumps
from pandas import DataFrame

app = Flask(__name__)
client = MongoClient("mongodb+srv://readonly:6LejsYJEHZDe5qZF@cluster0-6iwz3.mongodb.net/british-quiz-bot?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")

db = client['british-quiz-bot']
questions = db.questions
tests = db.tests


def get_tests_data():
    query = tests.find({}, { 
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
    query = questions.find({}, {
        'fields.question_text': True,
        'fields.airtable_id': True,
        'fields.A': True,
        'fields.B': True,
        'fields.C': True,
        'fields.D': True
    })

    rows = list(map( lambda x: dict(id=x['_id'], **x['fields']) , query ))
    return rows


def count_answers(tests, question_id):

    c = {
        'ChoseA' : 0,
        'ChoseB' : 0,
        'ChoseC' : 0,
        'ChoseD' : 0,
    }

    for test in tests:
        if test['question'] == question_id:
            if 'A' in test['answer']:
                c['ChoseA'] += 1
            elif 'B' in test['answer']:
                c['ChoseB'] += 1
            elif 'C' in test['answer']:
                c['ChoseC'] += 1
            elif 'D' in test['answer']:
                c['ChoseD'] += 1
            
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
    df_questions = df_questions.join(s_correct)
    df_questions.rename(columns={'answer' : 'Correct'}, inplace=True)
    df_questions = df_questions.join(s_wrong)
    df_questions.rename(columns={'answer' : 'Wrong'}, inplace=True)

    df_questions['Attemps'] = df_questions['Correct'] + df_questions['Wrong']
    df_questions['% Correct'] = df_questions['Correct'] / df_questions['Attemps']

    return questions


@app.route('/questions')
def questions():
    # retrieve records from db
    questions = get_questions_data()
    tests = get_tests_data()

    # perform calculations
    df_questions = prepare_data(questions, tests)
    json = df_questions.to_json(orient='records')

    # define response
    res = Response(json)
    res.headers['Content-Type'] = 'application/json'

    return res

@app.route('/')
def index():
    return render_template('index.html')
