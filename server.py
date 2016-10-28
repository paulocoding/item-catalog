from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

app = Flask(__name__)


# Routes
@app.route('/')
@app.route('/catalog')
def showCatalog():
    return "Catalog page."


# categories CRUD
@app.route('/catalog/category/new')
def newCategory():
    return "New category page."


@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    return "%s - Category page." % category_name


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
    return "%s>%s - Item page." % (category_name, item_name)


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
