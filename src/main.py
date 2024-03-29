from flask import Flask, request, jsonify, make_response
from  routes.slack_routes import slack_bp
from services.embedding_service import generate_embeddings 
from services.query_service import answer_question, list_assets, get_asset, delete_collection
from parsers.wiki_loader import WikiLoader

app = Flask(__name__, static_url_path='', static_folder='static')

app.register_blueprint(slack_bp, url_prefix='/slack')


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/feed', methods=['POST'])
def testgpt():
    item = request.get_json()
    generate_embeddings(item)
    return "Hello, World!"

@app.route('/answer', methods=['POST'])
def testGPTgetAnswer():
    item = request.get_json()
    answer_question(item)
    return "Hello, World!"

@app.route('/listassets', methods=['POST'])
def listAssets():
    item = request.get_json()
    list_assets(item)
    return "Hello, World!"

@app.route('/getasset', methods=['POST'])
def getAsset():
    item = request.get_json()
    get_asset(item)
    return "Hello, World!"

@app.route('/wiki', methods=['GET'])
def getWikiContent():
    wiki_url = 'https://wiki.corp.mycompany.com/display/~garg/Comparison+Between+Schedule+Vs+Event+Based+PA+job'
    wiki_loader = WikiLoader()
    content = wiki_loader.load_content(wiki_url)
    print(content)
    return "Hello, World!"

@app.route('/deletecollection', methods=['DELETE'])
def deleteCollection():
    # item = request.get_json()
    collection_name = "mybuddy_embeddings_C06992PM1LK"
    content = delete_collection(collection_name)
    return "Collection Deleted"

if(__name__ == '__main__'):
    app.run(debug=True,port=5000)
    print('Application Started')