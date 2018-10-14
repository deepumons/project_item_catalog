from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_setup import *

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Clear the data in tables if it already exist
session.query(User).delete()
session.query(Category).delete()
session.query(CategoryItem).delete()

# Create dummy users
user1 = User(name="Deepak Rajendran",
              email="urdeepak@gmail.com")
session.add(user1)
session.commit()

# Create default categories
category1 = Category(name="Televisions")
session.add(category1)
session.commit()

category2 = Category(name="Mobile Phones")
session.add(category2)
session.commit()

category3 = Category(name="Sporting Goods")
session.add(category3)
session.commit()

category4 = Category(name="Grocery")
session.add(category4)
session.commit()

category5 = Category(name="Movies")
session.add(category5)
session.commit()

#category6 = Category(name="Women's Fashion")
#session.add(category6)
#session.commit()

#category7 = Category(name="Sports, Fitness, Bags, Luggage")
#session.add(category7)
#session.commit()

#category8 = Category(name="Beauty, Health, Grocery")
#session.add(category8)
#session.commit()

#category9 = Category(name="Home, Kitchen, Pets")
#session.add(category9)
#session.commit()

#category10 = Category(name="Toys, Baby Products")
#session.add(category10)
#session.commit()

# Create category items

item1 = CategoryItem(name="Television",
	description="BPL 80 cm (32 inches) HD Ready LED TV",
    date=datetime.datetime.now(),
	category_id=1,
	user_id=1)
session.add(item1)
session.commit()

item2 = CategoryItem(name="Apple iPhone XS",
	description="The latest smart phone from Apple.",
    date=datetime.datetime.now(),
	category_id=2,
	user_id=1)
session.add(item2)
session.commit()

item3 = CategoryItem(name="Apple iPhone XS Max",
	description="The larger model of the latest smart phone from Apple. ",
    date=datetime.datetime.now(),
	category_id=2,
	user_id=1)
session.add(item3)
session.commit()

item4 = CategoryItem(name="Google Pixel 3",
	description="The latest smart phone from Google.",
    date=datetime.datetime.now(),
	category_id=2,
	user_id=1)
session.add(item4)
session.commit()

item5 = CategoryItem(name="Baseball bat",
	description="Strong base ball bat. Made of wood.",
    date=datetime.datetime.now(),
	category_id=3,
	user_id=1)
session.add(item5)
session.commit()

item6 = CategoryItem(name="Baseball Gloves",
	description="Synthetic gloves mean for baseball players.",
    date=datetime.datetime.now(),
	category_id=3,
	user_id=1)
session.add(item6)
session.commit()

session.add(item6)
session.commit()


print "The database has been populated and ready."
