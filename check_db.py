from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = session.query(Category).all()

# check all categories:
print "##############"
print "  Categories"
print "##############"
for cat in categories:
    print "%s:%s\n%s\ncreator: %s\n" % (cat.id,
                                        cat.name,
                                        cat.description,
                                        cat.user_id)

# check all items:
items = session.query(Item).all()
print "##############"
print "    Items"
print "##############"
for i in items:
    print "%s:%s\nqt:%s cat:%s:%s\n%s\ncreator: %s\n" % (i.id,
                                                         i.name,
                                                         i.quantity,
                                                         i.category_id,
                                                         i.category.name,
                                                         i.description,
                                                         i.user_id)
# check all users:
users = session.query(User).all()
print "##############"
print "    Users"
print "##############"
for u in users:
    print "%s: %s\nemail: %s\n%s" % (u.id, u.name, u.email, u.picture)
