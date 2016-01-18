import sys
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'cuser'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))
	creation = Column(Date)
	category_lst = relationship("Category", backref="cuser")
	item_lst = relationship("Item", backref="cuser")
	@property
	def serialize(self):
		#"""Return object data in easily serializeable format""
		return {
        	'name': self.name,
        	'id': self.id,
        	'email':self.email,
        	'item_lst':self.item_lst
    	}


class Category(Base):
	__tablename__ ='category'
	id =  Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	description = Column(String(500), nullable = False)
	creation = Column(Date)
	user_id = Column(Integer, ForeignKey('cuser.id'))
	rel_user = relationship(User)
	#item_lst = relationship("Item", backref="category")
	@property
	def serialize(self):
		#"""Return object data in easily serializeable format""
		return {
        	'name': self.name,
        	'id': self.id,
        	'description':self.description,
        	#list dictionaries have to be serialized before next level serializaton!!!
        	'item_lst':[i.serialize for i in self.item_lst]
    	}
    

class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	description = Column(String(550))
	creation = Column(Date)
	imageurl = Column(String(250))
	category_id = Column(Integer, ForeignKey('category.id'))
	rel_category = relationship(Category)
	user_id = Column(Integer, ForeignKey('cuser.id'))
	rel_user = relationship(User)
	category = relationship(Category, lazy='subquery', backref=backref('item_lst', uselist=True))

	@property
	def serialize(self):
	#return object data in easily serializeable format
		return {
			'name':self.name,
			'description': self.description,
			'category':self.category.name,
			'category_id':self.category_id,
			'user_id':self.user_id,
			'creation':self.creation.strftime('%m/%d/%Y'),
			'imageurl':self.imageurl,
			'id':self.id
		}

#############insert at end of file ########

engine = create_engine('postgresql://grader:grader@localhost/catalog')

Base.metadata.create_all(engine)

