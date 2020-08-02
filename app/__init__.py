from flask import Flask, render_template, jsonify, Response
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
client = MongoClient("mongodb+srv://readonly:6LejsYJEHZDe5qZF@cluster0-6iwz3.mongodb.net/british-quiz-bot?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")

db = client['british-quiz-bot']
questions = db.questions
tests = db.tests
users = db.users


def count_answer(tests, question_id):

    c = {
        'A' : 0,
        'B' : 0,
        'C' : 0,
        'D' : 0,
    }

    for test in tests:
        if test['question'] == question_id:
            if 'A' in test['answer']:
                c['A'] += 1
            elif 'B' in test['answer']:
                c['B'] += 1
            elif 'C' in test['answer']:
                c['C'] += 1
            elif 'D' in test['answer']:
                c['D'] += 1
            
    return c


def get_tests_data():
    query = tests.find({}, { 
        'questions.answer': True,
        'questions.question': True,
        'questions.answeredCorrectly': True
    })
    # .limit(10)

    # rows = list(map( lambda x: x['questions'] , query ))
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
        'fields.A': True,
        'fields.B': True,
        'fields.C': True,
        'fields.D': True
    })
    # .limit(10)

    rows = list(map( lambda x: dict(id=x['_id'], **x['fields']) , query ))
    return rows


def prepare_data(questions, tests):

    for question in questions:
        counts = count_answer(tests, question['id'])
        question.update(counts)

    return questions


@app.route('/')
def index():
    questions = get_questions_data()
    tests = get_tests_data()
    # rows = prepare_data(questions, tests)

    return jsonify(rows)
