import bottle
import sqlite3
import json

@bottle.get("/")
def index():
    return bottle.template('index')

# @bottle.get("/locations/<article_id:int>")
# def location(article_id):
#     return (Location
#         .select()
#         .where(Location.article == article_id)
#         .order_by(Location.confidence.desc(), Location.id.asc())
#         .dicts()
#         .get())

# @bottle.get("/categories/<article_id:int>")
# def category(article_id):
#     categories = (Category
#         .select()
#         .where(Category.article == article_id))

#     return {
#         "article": article_id,
#         "categories": [c.name for c in categories]
#     }

@bottle.get("/articles/")
def articles():
    conn = sqlite3.connect('violence.db')
    cursor = conn.cursor()

    l = cursor.execute("""
                        SELECT  location.lat, location.lng, location.returned_place, location.article_id
                        FROM    location
                        ORDER BY location.confidence DESC, location.id ASC
                       """)

    locations = {}
    for location in l.fetchall():
        # check if we already have entries for the article_id
        if not locations.get(location[3]):
            locations[location[3]] = (location[0], location[1], location[2])

    c = cursor.execute("""
                        SELECT  article.id, article.date, article.place, article.description, category.name
                        FROM    article
                            JOIN category ON article.id = category.article_id
                       """)

    articles = []
    for article in c.fetchall():
        article_id = article[0]
        if locations.get(article_id):
            articles.append({
                "id":           article_id,
                "date":         article[1],
                "place":        article[2],
                "description":  article[3],
                "category":     article[4],
                "lat":          locations[article_id][0],
                "lng":          locations[article_id][1],
                "place":        locations[article_id][2]
            })
    conn.close()
    return json.dumps(articles)

@bottle.get('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='static/')

if __name__ == "__main__":
    bottle.run(host="localhost", port=12345, reloader=True, debug=True)