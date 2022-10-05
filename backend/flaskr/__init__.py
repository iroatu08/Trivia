import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
import sys 
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def available_categories():
        categories = Category.query.order_by(Category.type).all()
        formatted_categories = {category.id: category.type for category in categories}
      
        if len(categories) == 0:
            abort(404)
      
        return jsonify({
          'success': True,
          'categories': formatted_categories,
       
        })
      
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def retrive_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}
        
        if len(current_questions) == 0:
            abort(404)
            
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': None,
            'categories': formatted_categories
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question is None:
                abort(404)
                
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
           
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                
            })
        except:
              abort(422)
              
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_questions():
        data = request.get_data()
        data = json.loads(data)
        new_question = data.get('question', None)
        new_answer = data.get('answer', None)
        new_difficulty = data.get('difficulty', None)
        new_category = data.get('category', None)
        
        try:
            question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            question.insert()
            
            return jsonify({
                'success': True,
                'created': question.id,
              
                })
        except:
               abort(422)
            
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        data = request.get_data()
        data = json.loads(data)
        searchTerm = data.get('searchTerm', None)
        
        try:
            questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm)))
            current_questions = paginate_questions(request, questions)
            
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                })
        except:
              print(sys.exc_info())
              abort(422)
            
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_in_category(category_id): 
        try: 
           questions = Question.query.filter_by(category=str(category_id)).all()
           current_questions = paginate_questions(request, questions)
           
           if len(questions) == 0:
                abort(404)
           
           return jsonify({
            'success': True,
            'questions':  current_questions,
            'total_questions':len(questions)
           
            })
        except:
           print(sys.exc_info())
           abort(422)

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
    @app.route('/quizzes', methods=['POST'])
    def questions_for_quiz(): 
        try:
            data = request.get_data()
            data = json.loads(data)
         
            previous_questions = data.get('previous_questions')
            category = data.get('quiz_category')
         
            if category['id'] == 0:
                 questions = Question.query.all()
                 questions = [question.format() for question in questions]
                 
            else:
                questions = Question.query.filter(Question.category == category['id']).all()
                questions = [question.format() for question in questions] 
            
            filter_questions = []
            for question in questions:
                if question['id'] not in previous_questions:
                    filter_questions+=[question]
         
                random_question = filter_questions[random.randint(0, len(filter_questions) -1)] if len(filter_questions) > 0 else ""
                
            return jsonify({
                    'success': True,
                    'question': random_question
                })
        except:
            print(sys.exc_info())
            abort(404)
                
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """ 
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )
    
    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    return app
