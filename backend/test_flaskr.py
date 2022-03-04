import os
import unittest
import json
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.session import close_all_sessions
from sqlalchemy.orm import sessionmaker

from flaskr import create_app
from models import setup_db, Question, Category
from pprint import pprint
import math

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('udacity:udacity@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_category = {
            "type": "test"
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    
    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.session.rollback()
            self.db.session.close()
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        res = self.client().get('/api/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data['categories']), 6)

    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    def test_get_question_by_pagination(self):
        res = self.client().get('/api/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        meta = data['meta']
        
        with self.app.app_context():
            count = self.db.session.query(Question).count()        
            last_page = math.ceil(count / 10)

        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(meta['last_page'], last_page)

        # if the page is outside the range we want to 404
        res = self.client().get('/questions?page=3')
        self.assertEqual(res.status_code, 404)

    def test_get_questions_by_category(self):
        res = self.client().get('/api/categories/1/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['current_category'], 'Science')
        self.assertEqual(data['total_questions'], 3)

    # def test_get_question_by_category(self):
    #     res = self.client().get('/questions')
    def test_get_questions_by_category_404(self):
        res = self.client().get('/api/categories/100/questions')
        self.assertEqual(res.status_code, 404)

    def test_searh_questions_by_term(self):
        res = self.client().get('/api/questions?search_term=actor')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)

    def test_search_term_404(self):
        res = self.client().get('/api/questions?search_term=banana')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data['questions']), 0)


    def test_start_quiz(self):
        # Quiz category all
        res = self.client().post('/api/quizzes', 
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                "previous_questions": [],
                "quiz_category": { "id": 0, "type": "All" }
            }))
        self.assertEqual(res.status_code, 201)
        # Quiz category science

    def test_start_quiz_with_categroy(self):
        res = self.client().post('/api/quizzes', 
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            "previous_questions": [],
            "quiz_category": { "id": 1, "type": "Science" }
        }))
        
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['question']['category'], '1')


    def test_start_quiz_with_category_and_previous_question(self):

        res = self.client().post('/api/quizzes', 
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            "previous_questions": [20, 21],
            "quiz_category": { "id": 1, "type": "Science" }
        }))

        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)

        self.assertEqual(data['question']['category'], '1')
        self.assertEqual(str(data['question']['id']), '22')

    def test_question_should_be_none_if_exhausted(self):
        res = self.client().post('/api/quizzes', 
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            "previous_questions": [20, 21, 22],
            "quiz_category": { "id": 1, "type": "Science" }
        }))

        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['question'], None)


    def test_add_quesiton(self):
        res = self.client().post('/api/questions', 
            data=json.dumps({
                "question": "What is the answer?",
                "answer": "The answer",
                "difficulty": 1,
                "category": "2"
            }),
            headers={'Content-Type': 'application/json'}), 
        self.assertEqual(res[0].status_code, 201)

    def test_delete_a_question(self):
        question = {
            "question": "What is the answer?",
            "answer": "The answer",
            "difficulty": 1,
            "category": "2"
        }
        
        with self.app.app_context():
            try:
                q = Question(**question)
                self.db.session.add(q)
                self.db.session.commit()
                id = q.id
            except:
                self.db.session.rollback()
            finally:
                self.db.session.close()
        
        res = self.client().delete(f'/api/questions/{id}') 
        self.assertEqual(res.status_code, 200)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()