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
@app.route('/catalog/category/new', methods=['GET', 'POST'])
def newCategory():
    return render_template('new_category.html')


@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        items = session.query(Item).filter_by(category_id=selected_category.id).order_by(Item.name).all()
        return render_template('category.html', category=selected_category, items=items)
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        return render_template('edit_category.html', category=selected_category)
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        return render_template('delete_category.html', category=selected_category)
    return render_template('404.html')


# items CRUD
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).order_by(Category.name).all()
    return render_template('new_item.html', categories=categories)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_category and selected_item:
        return render_template('item.html', category=selected_category, item=selected_item)
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    categories = session.query(Category).order_by(Category.name).all()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_item:
        return render_template('edit_item.html', categories=categories, item=selected_item)
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_category and selected_item:
        return render_template('delete_item.html', category=selected_category, item=selected_item)
    return render_template('404.html')


# Run app if run as script:
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
