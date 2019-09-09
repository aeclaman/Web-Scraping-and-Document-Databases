from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import os
import scrape_mars

app = Flask(__name__)

app.config['MONGO_URI'] = os.environ.get('MONGODB_URI') or "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)
# Use PyMongo to establish Mongo connection
#mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route("/")
def index():
     
    if (mongo.db.mars_data.count() == 0):
        # scrape the data for inital load of the mongo db
        mars_data = scrape_mars.scrape()
        mongo.db.mars_data.update({}, mars_data, upsert=True)
    
    # get scraped dictionary from mongo db.mars_db and send to html
    mars_dict = mongo.db.mars_data.find_one()

    return render_template("index.html", dict=mars_dict)

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_data = scrape_mars.scrape()

    print("Scrape complete, ready to update MongoDB")
    # Update the Mongo database using update and upsert=True
    mongo.db.mars_data.update({}, mars_data, upsert=True)

    print("MongoDB updated; rerounting to home screen...")
    # Redirect back to home page
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)