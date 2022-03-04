import os
from re import L
from unicodedata import category
from flask import Flask, request, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func
from flask_cors import CORS, cross_origin
import random

from itsdangerous import json

from models import setup_db, Question, Category

from pprint import pprint
import math

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
     # CORS Headers 
    cors = CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'application/json'
    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/categories', methods=['GET'])
    def get_all_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        categories = {}
        for category in Category.query.all():
            categories[category.id] = str(category.type)

        return jsonify({
            'success': True,
            'status_code': 200,
            'categories': categories
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        items_per_page = QUESTIONS_PER_PAGE
        
        page = request.args.get('page', 1, type=int)

        search_term = request.args.get('search_term', '', type=str)

        totalQuestions = Question.query.count()

        meta = {                
            'first_page': 1,   
            'current_page': page,
            'items_per_page': items_per_page,
            'last_page': math.ceil(totalQuestions / items_per_page),
            'total_questions': totalQuestions
        }

        if (page > meta['last_page']):
            abort(404)

        if (len(search_term)):
            query = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id)
            totalQuestions = query.count()
        else:
            query = Question.query.order_by(Question.id)

        # if query.count() == 0:
        #     abort(404)

        questions = query.paginate(page=page, per_page=items_per_page, error_out=False)

        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type

        return jsonify({
            'success': True,
            'status_code': 200,
            'meta': meta,
            'total_questions': totalQuestions,
            'questions': [ question.format() for question in questions.items],
            'categories': categories,
            'current_category': None,
        })
    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/api/questions/<id>', methods=['DELETE'])
    @cross_origin(supports_credentials=True)
    def delete_question(id):
        try:
            question = Question.query.get(id)
            db.session.delete(question)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            "status_code": 200
        }), 200

  

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/api/questions', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def create_question():
        data = json.loads(request.data)
        try: 
            question = Question(**data)
            db.session.add(question)
            db.session.commit()
        except: 
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
           "status_code": 201,
        }), 201
    
    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    """
    @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category_id(category_id):
        items_per_page = QUESTIONS_PER_PAGE
        page = request.args.get('page', 1, type=int)

        # check if category id exist or 404
        category = Category.query.get_or_404(category_id)

        query = Question.query.filter(Question.category == str(category_id)).order_by(Question.id)
        totalQuestions = query.count()
        questions = query.paginate(page=page, per_page=items_per_page, error_out=False)

        meta = {                
            'first_page': 1,   
            'current_page': page,
            'items_per_page': items_per_page,
            'last_page': math.ceil(totalQuestions / items_per_page),
            'total_questions': totalQuestions,
        }

        return jsonify({
            "status_code": 200,
            "meta": meta,
            'total_questions': totalQuestions,
            'current_category': category.type,
            "questions": [question.format() for question in questions.items]
        }), 200
    """
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/api/quizzes', methods=['POST', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def create_quiz():
        data = json.loads(request.data)

        if (None in data['quiz_category']):
            abort(404)

        category = data['quiz_category']['id']

        if (category != 0):
            query = Question.query.filter(Question.category == str(category))
        else:
            query = Question.query

        if len(data['previous_questions']):
            previous_questions = [str(id) for id in data['previous_questions']]
            query = query.filter(Question.id.notin_(previous_questions))
         
        if (query.count() == 0):
            # all questions have been exhausted and the game is over
            return jsonify({
                "question": None
            }), 201
        
        query = query.order_by(func.random())
        
        return jsonify({
            "question": query.first_or_404().format()
        }), 201



    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def server_error_404(e):
        # logging.exception('An error occurred during a request. %s', e)
        return jsonify({
            "message": "Couldnt find resource"
        }), 404

    @app.errorhandler(422)
    def server_error_422(e):
        # logging.exception('An error occurred during a request. %s', e)
        return jsonify({
            "message": "Couldnt create resource"
        }), 422
    

    return app

