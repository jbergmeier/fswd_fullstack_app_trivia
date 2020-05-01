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
      try:
        categories = Category.query.with_entities(Category.type).all()  
        result = {
            "success": True,
            "categories": categories
        }
        return jsonify(result)
        
      except:
        abort(422)

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
      try:
        # Define Start and End for Pagination
        page = request.args.get('page', 1, type=int)
        page_start = (page - 1) * QUESTIONS_PER_PAGE
        page_end = page_start + QUESTIONS_PER_PAGE
        # Get Data from DB
        questions = list(map(Question.format, Question.query.all()))
        categories = Category.query.with_entities(Category.type).all()
        total_number_questions = Question.query.count()

        result = jsonify({
            "success": True,
            "questions": questions[page_start:page_end],
            "total_questions": total_number_questions,
            "categories": categories
        })
        return result
      except:
        abort(422)

    '''
    # TODO: DONE Create an endpoint to DELETE question using a question ID.

    TEST: DONE When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
      try:
        question = Question.query.filter(Question.id==question_id).first()

        question.delete()
        questions = Question.query.with_entities(Question.id).all()

        return jsonify({
          "success": True, 
          "id_deleted": question_id
          }) #return redirect(url_for(request.url))
      except:
        abort(422)

    '''
    # TODO: DONE Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: DONE When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
      try:
        new_request = request.get_json()
        print(new_request)
        if(new_request['question'] == '' or new_request['answer'] == ''):
          abort(422)

        question = new_request['question']
        answer = new_request['answer']
        difficulty = new_request['difficulty']
        category = new_request['category']

        new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
        new_question.insert()

        return jsonify({'success': True, "message": "Question successful added"})

      except:
        abort(422)
      

    '''
    # TODO: DONE Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: DONE Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    @app.route('/questions/search', methods=['POST'])
    def question_search():
      try:
        categories = []
        request_data = request.get_json()
        search = request_data['searchTerm']
        search_term = "%{}%".format(search)
        # Get Questions based on Search Term
        questions = list(map(Question.format, Question.query.filter(Question.question.ilike(search_term)).all()))

        # Get Categories
        for i in questions:
          categories_temp = list(map(Category.format, Category.query.filter(i['category'] == Category.id).all()))
          for cat in categories_temp:
            if not (cat['type'] in categories):
              categories.append(cat['type'])

        # get total Number of Questions (after search)
        total_number_questions = Question.query.filter(Question.question.ilike(search_term)).count()
        
        result = jsonify({
            "success": True,
            "questions": questions,
            "total_questions": total_number_questions,
            "categories": categories
        })
        return result

      except:
        abort(422)

    '''
    # TODO: DONE Create a GET endpoint to get questions based on category.
    TEST: DONE In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_category(category_id):
      try:
        questions = list(map(Question.format, Question.query.filter(Question.category == category_id)))
        categories = Category.query.filter(Category.id == category_id).with_entities(Category.type).all()
        total_number_questions = Question.query.filter(Question.category == category_id).count()
        
        if(categories == []):
          abort(404)

        result = jsonify({
            "success": True,
            "questions": questions,
            "total_questions": total_number_questions,
            "categories": categories
        })
        return result
      
      except:
        abort(422)

    '''
    # TODO: DONE Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: DONE In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    @app.route('/quizzes', methods=['POST'])
    def post_quizzes():
      try:
        # Gather data
        data = request.get_json()
        category_id = data['quiz_category']['id']
        previous_questions = data['previous_questions']

        #Check if catepgry is set, if yes, which category
        if(category_id == 0):
          questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
          questions = Question.query.filter(Question.category == category_id).filter(Question.id.notin_(previous_questions)).all()
          print(questions)

        # checks if questions are still available. If not, send None to end the game
        if questions == []:
          next_question = None
        else:
          new_question = random.choices(questions, k=1)
          next_question = (Question.query.filter_by(id = new_question[0].id).one_or_none()).format()
        
        # Return to Frontend
        return jsonify({
          "success": True,
          "question": next_question
        })

      except:
        abort(422)
    '''
    # TODO: DONE Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        "success": False,
        "error": 404,
        "message" : "Resource not found"
      }), 404

    @app.errorhandler(422)
    def unprocessable(error):
      return jsonify({
        "success": False,
        "error": 422,
        "message" : "Unprocessable"
      }), 422

    @app.errorhandler(405)
    def not_allowed(error):
      return jsonify({
        "success": False,
        "error": 405,
        "message" : "Method not Allowed!!!"
      }), 405

    @app.errorhandler(400)
    def client_error(error):
      return jsonify({
        "success": False,
        "error": 400,
        "message" : "Bad Request"
      }), 400

    @app.errorhandler(500)
    def server_error(error):
      return jsonify({
        "success": False,
        "error": 500,
        "message" : "Internal Server error"
      }), 500


    return app
