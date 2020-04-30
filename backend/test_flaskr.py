import os
import unittest
import json
import random
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question= {
            'question': 'Is this a unittest?',
            'answer' : 'Yes, it is!',
            'difficulty': 2,
            'category': 1
        }
        
        self.search_questions = {
            'searchTerm': 'What'
        }
   
    def tearDown(self):
        """Executed after reach test"""
        # print('----------------')
        pass

    """
    TODO Write at least one test for each test for successful operation and for expected errors.
    """
    # ##################################
    # Categories GET
    # ##################################

    def test_1_get_categories(self):
        print('##### Check GET categories Endpoint #####')  
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])


    # ##################################
    # Questions GET/POST
    # ##################################

    def test_2_post_question(self):
        print('##### Check POST questions/ Endpoint #####')
        res = self.client().post('/questions', json=self.new_question)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)

        # Check if created question is in DB and the last entry (order by desc)
        last_entry = (Question.query.with_entities(Question.question).order_by(Question.id.desc()).first())
        self.assertTrue(last_entry[0], self.new_question['question'])


    def test_2a_get_questions(self):
        print('##### Check GET questions/ Endpoint #####')
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])


    # ##################################
    # Questions per Category
    # ##################################

    def test_3_get_question_of_category(self):
        print('##### Check GET questions/category_id/questions Endpoint #####')
        #Get Random Category ID
        category_id = (Question.query.with_entities(Question.category).all())
        rnd = random.randrange(0, (len(category_id)-1))
        print("Questions for Category: ", str(category_id[rnd][0]))
        # Exec
        res = self.client().get('/categories/' + str(category_id[rnd][0]) + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    
    def test_3a_get_question_of_category_fail(self):
        print('##### Check GET questions/category_id/questions Endpoint FAIL #####')
        res = self.client().get('/categories/1000000000000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

    
    # ##################################
    # Delete Questions
    # ##################################   

    def test_4_quizz

    # ##################################
    # Delete Questions
    # ##################################   

    def test_5_delete_question(self):
        print('##### Check DELETE questions/ Endpoint #####')
        last_entry_id = (Question.query.with_entities(Question.id).order_by(Question.id.desc()).first())
        res = self.client().delete('/questions/' + str(last_entry_id[0]))
        
        # Check if question has been successfully deleted
        t1 = Question.query.with_entities(Question.id).all()
        for i in t1:
            if(i[0] == last_entry_id[0]):
                self.assertTrue(False)
        self.assertEqual(res.status_code, 200)


    # ##################################
    # Questions Search
    # ##################################         

    def test_6_post_search(self):
        print('##### Check POST questions/search Endpoint #####')
        res=self.client().post('/questions/search', json=self.search_questions)
        data=json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        # Check if search Keyword is in results // lowercase to ignore capitalization like in the frontend
        if(data['questions']) != []:
            for question in data['questions']:
              self.assertIn(self.search_questions['searchTerm'].lower(), question['question'].lower())


    # ##################################
    # General
    # ##################################

    # Not existing Endpoint CHECK
    def test_99_get_question_of_category_fail(self):
        print('##### Check Bad Endpoint Response #####')
        res = self.client().get('/categories/1/questionEWNDE')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)   


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
