import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgres://oqwuuekwxaybaa:da0d9ca64f7678944056474cc94b3922b57ed434498a5902304e1096e047eff1@ec2-54-220-170-192.eu-west-1.compute.amazonaws.com:5432/d9k7jus30tbmvc'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'


