from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item


# db setup
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# app

app = Flask(__name__)

# Routes
@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(Item).order_by(Item.name).all()
    return render_template('catalog.html', categories=categories, items=items)


# categories CRUD
@app.route('/category/new')
@app.route('/catalog/category/new')
def newCategory():
    return "new category page"


@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        items = session.query(Item).filter_by(category_id=selected_category.id).order_by(Item.name).all()
        return render_template('category.html', category=selected_category, items=items)
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/edit')
def editCategory(category_name):
    return "edit category page."


@app.route('/catalog/<string:category_name>/delete')
def deleteCategory(category_name):
    return "delete category page."


# items CRUD
@app.route('/catalog/<string:category_name>/item/new')
def newItem(category_name):
    return "%s> New Item page." % (category_name)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    selected_item = session.query(Item).filter_by(name=item_name).order_by(Item.name).first()
    if selected_category and selected_item:
        return render_template('item.html', category=selected_category, item=selected_item)
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def editItem(category_name, item_name):
    return "%s>%s - Edit Item page." % (category_name, item_name)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete')
def deleteItem(category_name, item_name):
    return "%s>%s -Delete Item page." % (category_name, item_name)


# Run app if run as script:
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
