import os, csv
from turtle import update
import requests, json
from notion_client  import Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

FNAME= 'ratings.csv'
NOTION = Client(auth=os.getenv("NOTION_KEY"))
TOKEN = os.getenv("NOTION_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
FAVORITE = 5

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22"
}


class updateDB():

    def __init__(self, dbname, fname):
        self.dbname = dbname
        self.fname = fname
        self.content = requests.request("POST", f'https://api.notion.com/v1/databases/{DATABASE_ID}/query', headers=headers).json()

    def update(self):
        data = ingest_csv(self.fname)
        db_content = self.content['results']['properties']
        book_title = db_content['Book Title']
        favorites = db_content['Favorites']
        rating_avg = db_content['Avg. Rating']

        book_info = [book_title["title"]["text"]["content"], rating_avg["number"], favorites["number"]]
        
        unique_ratings = set([(line[0], line[1]) for line in data])
        if len(unique_ratings) != len(data):
            data = delete_duplicates(data)
        
        aggregate_ratings = summarize_data(data)
        
        for book, rating in aggregate_ratings.items():
            avg, fave_count = rating[0], rating[1]
            text = [book, avg, fave_count]
            if (text[0] == book_info[0]):
                if book_info[2] == FAVORITE: 
                    # update book_info
                # update book rating
        



# Add new page to database
def addItem(text, databaseId, headers):
    createPageURL = f"https://api.notion.com/v1/pages"

    data = {
        "parent": {"database_id": databaseId},
        "properties": {
            "Book Title": {
                "title": [
                    {
                        "text": {
                            "content": text[0]
                        }
                    }
                ]
            },
            "Avg. Rating": {"number": text[1]},
            "Favorites": {"number": text[2]}
        }
    }

    json_obj = json.dumps(data, indent=4)

    res = requests.request("POST", createPageURL, headers=headers, data=json_obj)

    # Handle cases where page cannot be added to the database
    if res.status_code!=200:
        print(f"ERROR +{res.status_code}: {res.text}.")
        return
    
    print(res.status_code)
    


def ingest_csv(filename):
    """
    Read CSV file and normalizes the data within it 
    to store to memory.
    """
    data = list()
    with open(filename, mode='r') as file:
        for line in csv.reader(file):
            line = normalize(line)
            data.append(line)
    return data


def normalize(data):
    """
    Gets rid of extra whitespace and ignores capitalization
    """
    data[0] = ' '.join(data[0].lower().split())
    data[1] = ' '.join(data[1].lower().split())
    return data


def delete_duplicates(data):
    """
    Creates a new dictionary of unique ratings in data
    by only keeping the most recent rating by a member
    that has read a book. 
    """
    no_dups = dict()
    for line in data:
        book, member, rating = line[0], line[1], line[2]
        pair = (book, member)
        no_dups[pair] = rating
    return [list(k) + [float(v)] for k, v in no_dups.items()]


def summarize_data(data):
    """
    Need to keep track of:
    1. Sum of ratings per book
    2. Number of times each book is rated
    3. Number of favorites per book

    Return all books with their average rating & number of "favorites"
    """
    unique_books = set([line[0] for line in data])

    ratings_sum = dict.fromkeys(unique_books, 0)
    read_count = dict.fromkeys(unique_books, 0)
    # Initialized values to 0 to handle edge case when a book has no "favorites"
    favorites_count = dict.fromkeys(unique_books, 0)

    # Calculate sum of ratings, number of times a book is rated, and number of favorites
    for line in data:
        book, rating = line[0], line[2]
        ratings_sum[book] += float(rating)
        read_count[book] += 1
        if rating == FAVORITE:
            favorites_count[book] += 1
    
    # Calculate average rating per book & aggregate above information into one dictionary
    aggregate_ratings = dict.fromkeys(unique_books)
    for book in aggregate_ratings.keys():
        avg = round(ratings_sum[book] / read_count[book], 2)
        aggregate_ratings[book]= [avg, favorites_count[book]]
        
    return aggregate_ratings


def main():
    db = updateDB("book ratings", FNAME)
    print(db.content)

    # Read csv file into memory
    # data = ingest_csv(FNAME)

    # # Delete duplicates but keep most recent duplicate entry
    # unique_ratings = set([(line[0], line[1]) for line in data])
    # if len(unique_ratings) != len(data):
    #     data = delete_duplicates(data)

    # # Calculate aggregations
    # aggregate_ratings = summarize_data(data)

    # # Write data to database
    # for book, rating in aggregate_ratings.items():
    #     avg, fave_count = rating[0], rating[1]
    #     text = [book, avg, fave_count]
    #     addItem(text, DATABASE_ID, headers)


if __name__=="__main__":
    main()
