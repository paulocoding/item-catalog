# Item Catalog
### A web application in python/flask for managing an item catalog

## backend : python 2.7, flask, jinja, Sqlite, sqlalchemy, oauth 2
## frontend : html5, css3, font-awesome, jquery

## Structure
* server.py - Server file, routes and requests handlers inside
* database_setup.py - Models and Database creation
* fill_database.py - Fills in the database with some data
* check_db.py - prints to the console the data currently on the database

* /templates - html templates

* /static - static files
  * /css - css files
  * /fonts - font files

## Use
* Create the database, by executing (on project folder):
```
  $ python database_setup.py
```
* Now you can add some sample data, by executing:
```
  $ python fill_database.py
```
* Run the server by executing:
```
  $ python server.py
```
* Open this link on a browser to use the application:
  * http://localhost:5000/

## JSON API endpoints for the app can be found here:
  * Full catalog of items:
    * http://localhost:5000/catalog/JSON
  * Categories:
    * http://localhost:5000/catalog/category/JSON
  * All items belonging to a specific category:
    * http://localhost:5000/catalog/<string:category_name>/JSON
  * A specific item:
    * http://localhost:5000/catalog/<string:category_name>/<string:item_name>/JSON
