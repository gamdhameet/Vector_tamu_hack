from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from sklearn.preprocessing import normalize

# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# MongoDB Atlas Connection
MONGODB_URI = "mongodb+srv://sreevikramr:b9baMr-Rk-D_tm_@tamuhack25db.b2or5.mongodb.net/?retryWrites=true&w=majority&appName=tamuHack25DB"
client = MongoClient(MONGODB_URI)

# Database and Collections
DB1 = client["tamuHack25DB"]
collections = {
    "data_embeddings": DB1["data_embeddings"],
    "all_dep_comb": DB1["all_dep_comb"],
    "Teachers_RMP": DB1["Teachers_RMP"]
}

@app.route('/search', methods=['POST'])
def search():
    """
    Combines vectorization and MongoDB search.
    Expects a JSON payload with a "query" field.
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Please provide 'query' in the request body"}), 400

    query_text = data['query']

    # Generate embeddings
    query_vector = model.encode(query_text)
    query_vector = normalize([query_vector])[0].tolist()

    # Search results from all collections
    results = {}

    for name, collection in collections.items():
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "Embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 10
                }
            }
        ]
        query_results = list(collection.aggregate(pipeline))

        formatted_results = []
        for doc in query_results:
            if name == "data_embeddings":
                formatted_results.append({
                    "Title": doc.get("Title"),
                    "Content": doc.get("Specific Content"),
                    "URL": doc.get("URL"),
                    "Score": round(doc.get("score", 0), 4)
                })
            elif name == "teachers_RMP":
                formatted_results.append({
                    "Name": doc.get("Name"),
                    "GPA": doc.get("GPA"),
                    "COURSE": doc.get("Course"),
                })
            elif name == "Teachers_RMP":
                formatted_results.append({
                    "Name": doc.get("Name"),
                    "comment": doc.get("comment"),
                    "Attendance Mandatory": doc.get("attendanceMandatory"),
                    "Rating": doc.get("clarityRating"),
                    "Helpfulness": doc.get("helpfulRating"),
                    "Difficulty": doc.get("difficultyRating"),
                    "ratingTags": doc.get("ratingTags"),
                })

        results[name] = formatted_results

    return jsonify(results)

if __name__ == '__main__':
    # Uncomment this line when deployingpublicly
    app.run(host='0.0.0.0', port=5000, debug=True)

    # **Local Testing using Flask's test client**
    # with app.test_client() as client:
    #     test_query = {"query": "Who is the best CS professor?"}
    #     response = client.post('/search', json=test_query)
    #     print("Testing Search with hardcoded input:")
    #     print(response.get_json())  # Print the response for debugging
