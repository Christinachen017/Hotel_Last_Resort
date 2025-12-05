from flask import Flask, render_template, request, redirect, url_for, make_response


# instantiate the app
app = Flask(__name__)

# Create a list called categories. The elements in the list should be lists that contain the following information in this order:
#   categoryId
#   categoryName
#   An example of a single category list is: [1, "Biographies"]
categories = [
    [1, "Fantasy"],
    [2, "Sci-Fi"],
    [3, "Fiction"],
    [4, "Romance"]
]

# Create a list called books. The elements in the list should be lists that contain the following information in this order:
#   bookId     (you can assign the bookId - preferably a number from 1-16)
#   categoryId (this should be one of the categories in the category dictionary)
#   title
#   author
#   isbn
#   price      (the value should be a float)
#   image      (this is the filename of the book image.  If all the images, have the same extension, you can omit the extension)
#   readNow    (This should be either 1 or 0.  For each category, some of the books (but not all) should have this set to 1.
#   An example of a single category list is: [1, 1, "Madonna", "Andrew Morton", "13-9780312287863", 39.99, "madonna.png", 1]
books = [
    # Fantasy
    [1, 1, "Dungeon Crawler Carl", "Matt Dinniman", "9780593820247", 14.99, "dcc.png", 1],
    [2, 1, "Quicksilver", "Callie Hart", "9781538774199", 13.28, "quicksilver.png", 0],
    [3, 1, "The Alchemist: A Fable About Following Your Dream", "Paulo Coelho", "9780722532935", 10.65, "alchemist.png", 1],
    [4, 1, "A Court of Thorns and Roses", "Sarah J Maas", "9781635575569", 8.99, "court.png", 0],
    # Sci-Fi
    [5, 2, "The Ballad of Songbirds and Snakes (A Hunger Games Novel)", "Suzanne Collins", "9781338635171", 10.05, "songbird.png", 1],
    [6, 2, "The Midnight Library", "Matt Haig", "9781443455879", 12.74, "midnight.png", 0],
    [7, 2, "Fahrenheit 451", "Ray D Bradbury", "9781451673319", 8.50, "451.png", 1],
    [8, 2, "House of Sky and Breath", "Sarah J Maas", "9781635574074", 11.49, "sky.png", 0],
    # Fiction
    [9, 3, "Atmosphere: A GMA Book Club Pick: A Love Story", "Taylor Jenkins Reid", "9780593158715", 18.07, "atmo.png", 1],
    [10, 3, "The Housemaid Is Watching", "Freida McFadden", "9781464221132", 10.65, "housemaid.png", 0],
    [11, 3, "Red Rising", "Pierce Brown", "9780345539809", 10.65, "red.png", 1],
    [12, 3, "The Sweetness of Water", "Nathan Harris", "9780316461276", 34.70, "water.png", 0],
    # Romance
    [13, 4, "Broken Country (Reese's Book Club)", "Clare Leslie Hall", "9781668078181", 16.85, "broken_country.png", 0],
    [14, 4, "Reminders of Him", "Colleen Hoover", "9781542025607", 6.41, "reminders_of_him.png", 1],
    [15, 4, "The Great Alone", "Kristin Hannah", "9781250229533", 8.50, "the_great_alone.png", 0],
    [16, 4, "Verity", "Colleen Hoover", "9781791392796", 0.99, "verity.png", 1]
]


# set up routes
@app.route('/')
def home():
    #Link to the index page.  Pass the categories as a parameter
    return render_template('index.html', categories=categories)

@app.route('/category')
def category():
    # Store the categoryId passed as a URL parameter into a variable
    categoryId = int(request.args.get('categoryId', 1))
    
    # Create a new list called selected_books containing a list of books that have the selected category
    selected_books = [book for book in books if book[1] == categoryId]
    
    # Find the selected category name
    selectedCategory = None
    for category in categories:
        if category[0] == categoryId:
            selectedCategory = category
            break
    
    # Link to the category page.  Pass the selectedCategory, categories and books as parameters
    return render_template('category.html', selectedCategory=selectedCategory, categories=categories, selected_books=selected_books)

@app.route('/search')
def search():
    #Link to the search results page.
    return render_template()

@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e) # render the edit template


if __name__ == "__main__":
    app.run(debug = True)
