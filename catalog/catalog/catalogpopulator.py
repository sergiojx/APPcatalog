from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Base, User, Category, Item
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random


engine = create_engine('postgresql://grader:grader@localhost/catalog')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


#This method will make a random creation date 
def CreateRandomAge():
	today = datetime.date.today()
	days_old = randint(0,540)
	creation = today - datetime.timedelta(days = days_old)
	return creation

#Add Users
user1 = User(name = "Elvis", 
				email = "elvis@mail.com", 
				picture = "http://icons.iconarchive.com/icons/iconka/persons/128/elvis-icon.png",
				creation = CreateRandomAge())
session.add(user1)
session.commit()

user2 = User(name = "Holmes", 
				email = "holmes@mail.com", 
				picture = "http://icons.iconarchive.com/icons/iconka/persons/128/holmes-icon.png",
				creation = CreateRandomAge())
session.add(user2)
session.commit()

user3 = User(name = "Monroe", 
				email = "monroe@mail.com", 
				picture = "http://icons.iconarchive.com/icons/iconka/persons/128/monroe-icon.png",
				creation = CreateRandomAge())
session.add(user3)
session.commit()

user4 = User(name = "Terminator", 
				email = "terminator@mail.com", 
				picture = "http://icons.iconarchive.com/icons/iconka/persons/128/terminator-icon.png",
				creation = CreateRandomAge())
session.add(user4)
session.commit()

#Add Category
category1 = Category(name='System On Module (SoM)',
						description = """System On Module: A computer-on-module (COM) or system on module (SOM) is a type of single-board computer (SBC), a subtype of an embedded computer system. An extension of the concept of system on chip (SoC) and system in package (SiP), COM lies between a full-up computer and a microcontroller in nature.""",
						creation = CreateRandomAge(),
						cuser = user1)
session.add(category1)
session.commit()
category2 = Category(name = 'Single Board Computer (SBC)',
						description = """Single Board Computer: A single-board computer (SBC) is a complete computer built on a single circuit board, with microprocessor(s), memory, input/output (I/O) and other features required of a functional computer. Single-board computers were made as demonstration or development systems, for educational systems, or for use as embedded computer controllers. Many types of home computer or portable computer integrated all their functions onto a single printed circuit board.""",
						creation = CreateRandomAge(),
						cuser = user2)
session.add(category2)
session.commit()
#Add Some items
item1 = Item(name = 'COREG25',
				description = """CORE9G25 is a cost-effective System-on-Module (SoM) thought of to drastically reduce the development time needed to design a low-power and low-EMI Linux Embedded device.""",
				imageurl = "http://armdevs.com/image/CORE9G25/interface.jpg",
				cuser = user4,
				creation = CreateRandomAge(),
				category = category1)
session.add(item1)
session.commit()
item2 = Item(name = 'DragonBoard 410c',
				description = """The DragonBoard 410c is the first development board based on a Qualcomm Snapdragon 400 series processor. It features advanced processing power, Wi-Fi, Bluetooth connectivity, and GPS, all packed into a board the size of a credit card. Based on the 64-bit capable Snapdragon 410 processor.""",
				imageurl = "https://developer.qualcomm.com/sites/default/files/attachments/db410c-blue-2a.png",
				cuser = user4,
				creation = CreateRandomAge(),
				category = category2)
session.add(item2)
session.commit()
session.close()
	
