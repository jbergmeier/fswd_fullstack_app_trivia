import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    # TODO: DONE Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app)

    # TODO: DONE Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # TODO: DONE Create an endpoint to handle GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.with_entities(Category.type).all()  
        result = {
            "success": True,
            
            "categories": categories
        }
        return jsonify(result)

        '''
      # TODO: DONE Create an endpoint to handle GET requests for questions,
      including pagination (every 10 questions).
      This endpoint should return a list of questions,
      number of total questions, current category, categories.

      TEST: DONE At this point, when you start the application
      you should see questions and categories generated,
      ten questions per page and pagination at the bottom of the screen for three pages.
      Clicking on the page numbers should update the questions.
      '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # Define Start and End for Pagination
        page = request.args.get('page', 1, type=int)
        page_start = (page - 1) * QUESTIONS_PER_PAGE
        page_end = page_start + QUESTIONS_PER_PAGE
        # Get Data from DB
        questions = list(map(Question.format, Question.query.all()))
        categories = Category.query.with_entities(Category.type).all()
        total_number_questions = Question.query.count()

        result = {
            "success": True,
            "questions": questions[page_start:page_end],
            "total_questions": total_number_questions,
            "categories": categories
        }
        return result

    '''
    # TODO: Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
      print(request.base_url)
      try:
        delete_entry = request.get_json()
        question = Question.query.filter(Question.id==question_id).first()

        question.delete()
        questions = Question.query.with_entities(Question.id).all()

        return redirect(url_for(request.url))
      except:
        
        return jsonify({"success": False})

    '''
    # TODO: Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
      error = False
      try:
        new_request = request.get_json()
        question = new_request['question']
        answer = new_request['answer']
        difficulty = new_request['difficulty']
        category = new_request['category']

        new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
        new_question.insert()

        return jsonify({'success': True, "message": "Question successful added"})

      except:
        error = True
      if error:
        return jsonify({"error" : True, "message": "An error has occured"})
      

    '''
    # TODO: Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    '''
    # TODO: Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def questions_category(category_id):
      # Define Start and End for Pagination
        page = request.args.get('page', 1, type=int)
        page_start = (page - 1) * QUESTIONS_PER_PAGE
        page_end = page_start + QUESTIONS_PER_PAGE
        # Get Data from DB
        questions = list(map(Question.format, Question.query.filter(Question.category == category_id)))
        categories = Category.query.filter(Category.id == category_id).with_entities(Category.type).all()
        total_number_questions = Question.query.filter(Question.category == category_id).count()

        result = {
            "success": True,
            "questions": questions[page_start:page_end],
            "total_questions": total_number_questions,
            "categories": categories
        }
        return result


    '''
    # TODO: Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    '''
    # TODO: Create error handlers for all expected errors
    including 404 and 422.
    '''

    return app
