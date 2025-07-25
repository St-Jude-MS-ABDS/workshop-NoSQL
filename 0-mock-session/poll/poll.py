from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware
import yaml
import getpass
import qrcode
import os
from io import StringIO, BytesIO
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

# Check if in the codespace environment
# https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace?tool=webui
mongo_uri = None
db_name = "mock_session"
collection_name = "pre_class_poll"
question_id = "database-nonsense-poll"
qr_code_img = None

class preflight_class():
    def __init__(self):
        self.url = None
        self.mongo_uri = None
    def _get_question(self):
        # Load the question from the YAML file
        with open("question.yaml", "r") as file:
            question = yaml.safe_load(file)
        return question
    def _in_codespace(self):
        return os.getenv("CODESPACES", False) == 'true'
    def get_mongo_uri(self):
        # ask user to input MongoDB URI, with hidden input
        self.mongo_uri = getpass.getpass("Please enter your MongoDB URI: ")
    def _check_mongo(self):
        # Check if the MongoDB URI is working
        try:
            _client = MongoClient(self.mongo_uri)
            _client.admin.command('ping')
            question = self._get_question()
            _client[db_name][collection_name].replace_one({"id": question["id"]}, question, upsert=True)
            _client.close()
            print("MongoDB is connected successfully.")
        except Exception as e:
            print("MongoDB is not connected, please check your connection string.")
            raise e

    def get_web_url(self):
        if self._in_codespace():
            codespace_name = os.getenv("CODESPACE_NAME")
            port = 8000 # as specified in .devcontainer/devcontainer.json
            domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
            self.url = "https://{codespace_name}-{port}.{domain}".format(codespace_name=codespace_name, port=port, domain=domain)
        else:
            self.url = "http://localhost:8000"
    def generate_qr_code(self):
        if not self.url:
            self.get_web_url()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        # save to file
        global qr_code_img
        qr_code_pil = qr.make_image(fill_color="black", back_color="white")
        qr_code_img = BytesIO()
        qr_code_pil.save(qr_code_img, format='PNG')
        qr_code_img.seek(0)  # Reset the stream position to the beginning
        
        # use stringio to print ascii QR code
        output = StringIO()
        qr.print_ascii(out=output)
        output.seek(0)
        
        ascii_qr = output.read()
        print(f"Service url: {self.url}")
        print("Scan this QR code to access the poll:")
        print("")
        print(ascii_qr)
        print("")

    def check(self):
        self.get_mongo_uri()
        self._check_mongo()
        self.get_web_url()
        self.generate_qr_code()

preflight = preflight_class()
preflight.check()
app = FastAPI()

# Allow frontend access from different origins (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB Atlas
client = MongoClient(preflight.mongo_uri)
db = client[db_name]
collection = db[collection_name]
@app.post("/vote")
async def vote(statements: list[str] = Form(...)):
    collection.update_one(
        {"id": question_id},
        {"$push": {"votes": statements}}, # anonymous voting
    )
    return RedirectResponse(url="/results", status_code=303)

@app.get("/qr.png")
async def get_qr_code():
    if qr_code_img:
        qr_code_img.seek(0)  # Reset the stream position to the beginning
        return StreamingResponse(qr_code_img, media_type="image/png")
    return {"error": "QR code not generated yet."}

@app.get("/", response_class=HTMLResponse)
async def poll_form():
    question = collection.find_one({"id": question_id})
    return f"""
    <html>
        <head>
            <title>Database Poll</title>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    max-width: 600px;
                    margin: 2em auto;
                    padding: 1em;
                    background: #f9f9f9;
                    color: #333;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #2c3e50;
                }}
                form ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                form li {{
                    margin: 10px 0;
                }}
                button {{
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    font-size: 1em;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <h2>{question['question']}</h2>
            <form action="/vote" method="post">
                <ul>
                    {"".join(f'<li><label><input type="checkbox" name="statements" value="{option}"> {option}</label></li>' for option in question['options'])}
                </ul>
                <button type="submit">Submit Vote</button>
            </form>
            <img src="qr.png" alt="QR Code to Poll" style="margin-top: 20px; max-width: 360px; height: auto;">
        </body>
    </html>
    """

@app.get("/results", response_class=HTMLResponse)
async def show_results():
    results = collection.aggregate([
        {"$match": {"id": question_id}},
        {"$unwind": "$votes"},
        {"$unwind": "$votes"},
        {"$group": {"_id": "$votes", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    html = """
    <html>
        <head>
            <title>Poll Results</title>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    max-width: 600px;
                    margin: 2em auto;
                    padding: 1em;
                    background: #f9f9f9;
                    color: #333;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #27ae60;
                }}
                li {{
                    margin: 8px 0;
                }}
                a {{
                    display: inline-block;
                    margin-top: 1em;
                    text-decoration: none;
                    color: #3498db;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h2>Poll Results</h2>
            <ul>
    """
    for result in results:
        html += f"<li>{result['_id']}: {result['count']} votes</li>"
    html += "</ul><a href='/'>← Back to poll</a></body></html>"
    return html
