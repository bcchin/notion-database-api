# Book Ratings
Reads a CSV file containing book ratings and populates the information into a specified Notion Database through API requests.

## How to Run the Project:
1. Download and unzip the folder.
2. Open terminal and navigate to the folder
2. Create a virtual environment within the folder and activate it.
3. Install all dependencies in `requirements.txt`
4. Run `main.py`

## Libraries Used
`python-dotenv`
- To access environment variables (i.e. Notion integration token and database id) stored in `.env`

### Some Challenges Faced:
Initially, I struggled with deciding how to aggregate ratings such that I could calculate the average rating for each book and keep track of the number of "favorites" for each book. I resolved this by writing down what I needed, as seen in the docstring for `summarize_data()`, and then choosing to use dictionaries to manage all the unique values for each book in order to maintain code readability.

### Suggestions for Notion API documentation:
I thought the documentation was actually really clear. I found the cURL examples for each request to be especially helpful in creating a request to the Notion API. 