"""Cleans up the Database and fills it with some default data."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# WARNING #
# Deleting all items in db! #
session.query(Item).delete()
session.query(Category).delete()

# Create some categories :
cat1 = Category(name="fruit", description="The best selection of fruit from all\
 over the world", user_id=1)
session.add(cat1)
session.commit()

cat2 = Category(name="vegetables", description="Healthy and fresh!", user_id=1)
session.add(cat2)
session.commit()

cat3 = Category(name="cookies", description="Chocolate chip cookies, peanut\
 butter cookies, butter cookies, find them all here!", user_id=1)
session.add(cat3)
session.commit()

# Create some items:
item1 = Item(name="Banana", description="Yellow and yummy", quantity=20,
             category_id=1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Apple", description="Red and juicy", quantity=35,
             category_id=1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Orange", description="You cant taste the sun in them!",
             quantity=5, category_id=1, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Leek", description="Green and fresh!",
             quantity=12, category_id=2, user_id=1)
session.add(item4)
session.commit()

item5 = Item(name="Broccoli", description="Kid's favorite!",
             quantity=20, category_id=2, user_id=1)
session.add(item5)
session.commit()

item6 = Item(name="Chokies", description="Chocolate chip cookies",
             quantity=8, category_id=3, user_id=1)
session.add(item6)
session.commit()

item7 = Item(name="Peanuties", description="Peanut butter cookies",
             quantity=34, category_id=3, user_id=1)
session.add(item7)
session.commit()

print "Categories and items Added!"
