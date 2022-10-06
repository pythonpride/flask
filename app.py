from flask import request, jsonify
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (Column,DateTime,ForeignKey,Integer,String,create_engine,func)

engine = create_engine('postgresql://') #заполнить данными!
Base = declarative_base()
Session = sessionmaker(bind=engine)
app = Flask('app')


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    registration_time = Column(DateTime, server_default=func.now())

    
class  Advertisement(Base):
    __tablename__ = "advertisement"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(ForeignKey(User.id))

Base.metadata.create_all(engine)


class UserView(MethodView):

    def get(self, user_id):       
        with Session() as session:
           user = session.query(User).get(user_id)           
           return jsonify({
                'email': user.email
                               
            })

    def post(self):
        user_data = request.json
        with Session() as session:
            new_user = User(email=user_data['email'], password=user_data['password'])
            session.add(new_user)
            session.commit()
            return jsonify({'status': 'ok', 'id': new_user.id})


class AdvView(MethodView):

    def get(self, adv_id):
        with Session() as session:
            adv = session.query(Advertisement).get(adv_id)  
            return jsonify({
                'title': adv.title,
                'registration_time': adv.created_at.isoformat(),
                'description': adv.description,
                'owner': adv.owner
            })

    def post(self):
        adv_data = request.json
        with Session() as session:
            new_adv = Advertisement(title=adv_data['title'], description=adv_data['description'],owner=adv_data['owner'])
            session.add(new_adv)
            session.commit()
            return jsonify({'status': 'ok', 'id': new_adv.id})

    def patch(self, adv_id):
        adv_data = request.json
        with Session() as session:
            adv = session.query(Advertisement).get(adv_id) 
            for key, value in adv_data.items():
                setattr(adv, key, value)
            session.commit()
        return jsonify({'status': 'ok'})

    def delete(self, adv_id):
        with Session() as session:
            adv = session.query(Advertisement).get(adv_id) 
            session.delete(adv)
            session.commit()
        return jsonify({'status': 'Ok'})



app.add_url_rule(
    "/users/", view_func=UserView.as_view("register_user"), methods=["POST"]
)
app.add_url_rule(
    "/users/<int:user_id>/", view_func=UserView.as_view("get_user"), methods=["GET"]
)

app.add_url_rule(
    "/adv/", view_func=AdvView.as_view("create_adv"), methods=["POST"]
)

app.add_url_rule(
    "/adv/<int:adv_id>/", view_func=AdvView.as_view("get_adv"), methods=["GET", "PATCH", "DELETE"]
)
app.run()