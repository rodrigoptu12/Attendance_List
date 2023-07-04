from flask import Flask, render_template, request, redirect, session, jsonify
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from models.question import Question
from models.item import Item
from models import db


class QuestionController(Resource):

    def post(self):
        # obtem os dados enviados com a solicitação
        data = request.get_json()

        # cria uma nova questão com os dados recebidos
        new_question = Question(command=data['command'],
                                answer_key=data['answer_key'],
                                question_type=data['question_type'])
        # adiciona a nova questão na sessão do banco de dados
        db.session.add(new_question)
        db.session.commit()

        # cria itens para a questão
        for item in data['items']:
            new_item = Item(text=item['text'], question_id=new_question.id)
            db.session.add(new_item)
            db.session.commit()

        # resgata a questão e seus itens do banco de dados
        question = Question.query.get(new_question.id)
        question_dict = {
            'id': question.id,
            'command': question.command,
            'items': [{
                'id': i.id,
                'text': i.text
            } for i in question.items],
            'answer_key': question.answer_key,
            'question_type': question.question_type
        }

        # retorna a questão e seus itens como JSON
        return jsonify(question_dict)

    def get(self):
        # Obtain all the questions from the database
        questions = Question.query.all()

        # Transform the SQLAlchemy objects into dictionaries
        list_of_questions = []
        for question in questions:
            question_dict = {
                'id':
                question.id,
                'command':
                question.command,
                'answer_key':
                question.answer_key,
                'question_type':
                question.question_type,
                'items': [{
                    'id': item.id,
                    'text': item.text
                } for item in question.items]
            }
            list_of_questions.append(question_dict)

        # Return the data as a JSON
        return jsonify(list_of_questions)