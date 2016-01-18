import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from sqlalchemy.sql import select
import datetime

def getDbSession():
	engine = create_engine('postgresql://grader:grader@localhost/catalog')
	Base.metadata.bind = engine 
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	return session


def closeSession(session):
	session.close()


def getAllCategory():
	s = getDbSession()
	catlst = s.query(Category).order_by(Category.creation.desc())
	closeSession(s)
	return catlst


def getRecetItems(qty):
	s = getDbSession()
	catlst = s.query(Item).order_by(Item.creation.desc()).limit(qty)
	closeSession(s)
	return catlst

def getCategoryById(category_id):
	s = getDbSession()
	category = s.query(Category).filter_by(id=category_id).one()
	closeSession(s)
	return category

def getItemById(item_id):
	s = getDbSession()
	item = s.query(Item).filter(Item.id==item_id).one()
	closeSession(s)
	return item

def getItemLstByCategoryId(category_id):
	s = getDbSession()
	itemlst = s.query(Item).filter(Item.category_id==category_id).all()
	closeSession(s)
	return itemlst

def createUser(login_session):
	newUser = User(name=login_session['username'],
					email=login_session['email'],
					picture=login_session['picture'],
					creation=datetime.date.today())
	addNewUser(newUser)
	user = getUserByemail(login_session['email'])
	#user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id


def addNewUser(newUser):
	s = getDbSession()
	s.add(newUser)
	s.commit()
	closeSession(s)

def addNewItem(newItem):
	s = getDbSession()
	s.add(newItem)
	s.commit()
	closeSession(s)

def removeItemById(item_id):
	s = getDbSession()
	item = s.query(Item).filter(Item.id == item_id).one()
	s.delete(item)
	s.commit()
	closeSession(s)

def updateItemById(item_id, new_name, new_description, new_imgURL, new_category_id):
	s = getDbSession()
	item = s.query(Item).filter(Item.id == item_id).one()
	item.name = new_name
	item.description = new_description
	item.imageurl = new_imgURL
	item.category_id = new_category_id
	s.add(item)
	s.commit()
	closeSession(s)


def getUserInfo(user_id):
	user = getUserById(user_id)
	#user = session.query(User).filter_by(id=user_id).one()
	return user


def getUserID(email):
	try:
		user = getUserByemail(email)
		#user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

	
def getUserByemail(user_email):
	s = getDbSession()
	user = s.query(User).filter_by(email=user_email).one()
	closeSession(s)
	return user


def getUserById(user_id):
	s = getDbSession()
	user = s.query(User).filter_by(id=user_id).one()
	closeSession(s)
	return user








