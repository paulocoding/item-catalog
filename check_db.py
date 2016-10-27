from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = session.query(Category).all()

# check all categories:
print "##############"
print "  Categories"
print "##############"
for cat in categories:
    print "%s:%s\n%s\n" % (cat.id, cat.name, cat.description)

# check all items:
items = session.query(Item).all()
print "##############"
print "    Items"
print "##############"
for i in items:
    print "%s:%s\nqt:%s cat:%s:%s\n%s\n" % (i.id, i.name, i.quantity,
                                            i.category_id, i.category.name,
                                            i.description)
# item2 = Item(name="Apple", description="Red and juicy", quantity=35,
#              category_id=1)
# session.add(item2)
# session.commit()
