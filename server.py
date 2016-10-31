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
    if request.method == 'GET':
        return render_template('new_category.html')
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_category = Category(name=name, description=description)
        session.add(new_category)
        session.commit()
        return redirect(url_for('showCatalog'))


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
        if request.method == 'GET':
            return render_template('edit_category.html', category=selected_category)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            selected_category.name = name
            selected_category.description = description
            session.add(selected_category)
            session.commit()
            return redirect(url_for('showCategory', category_name=name))
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        if request.method == 'GET':
            return render_template('delete_category.html', category=selected_category)
        if request.method == 'POST':
            session.delete(selected_category)
            session.commit()
            return redirect(url_for('showCatalog'))
    return render_template('404.html')


# items CRUD
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    if request.method == 'GET':
        categories = session.query(Category).order_by(Category.name).all()
        return render_template('new_item.html', categories=categories)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category_id = request.form['category']
        quantity = request.form['quantity']
        new_item = Item(name=name,
                        description=description,
                        quantity=quantity,
                        category_id=category_id)
        session.add(new_item)
        session.commit()
        return redirect(url_for('showItem', category_name=new_item.category.name, item_name=name))


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
        if request.method == 'GET':
            return render_template('edit_item.html', categories=categories, item=selected_item)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category_id = request.form['category']
            quantity = request.form['quantity']
            selected_item.name = name
            selected_item.description = description
            selected_item.category_id = category_id
            selected_item.quantity = quantity
            session.add(selected_item)
            session.commit()
            return redirect(url_for('showItem', category_name=selected_item.category.name, item_name=name))
    return render_template('404.html')


@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_category and selected_item:
        if request.method == 'GET':
            return render_template('delete_item.html', category=selected_category, item=selected_item)
        if request.method == 'POST':
            session.delete(selected_item)
            session.commit()
            return redirect(url_for('showCatalog'))
    return render_template('404.html')


# Run app if run as script:
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
