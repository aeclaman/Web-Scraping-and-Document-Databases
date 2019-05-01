from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

app = Flask(__name__)

# Create connection variable
#conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
#client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
#db = client.mars_db

# Use flask_pymongo to set up mongo connection
#app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
#mongo = PyMongo(app)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

# Or set inline
# mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")


@app.route("/")
def index():
    # Here, db.students refers to the collection 'classroom '
    mars_dict = mongo.db.mars_data.find_one()
    # Get html string to remove first and last quotes around html and pass directly to html
    #value = mars_dict.get('mars_facts')
    #facthtml = value[1:-1]

    # Iterate through each student in the collection
    for x in mars_dict:
        print(x)
  
    return render_template("index.html", dict=mars_dict) #, facthtml=facthtml)

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True
    mongo.db.mars_data.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)