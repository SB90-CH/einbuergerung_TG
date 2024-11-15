import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
You are an intelligent assistant that answers questions and provides support. Your role is: Specialist for naturalizations in the Canton of Thurgau.
You aim to provide answers that are as precise and accurate as possible. 
Your goal is to ensure that the questioner receives answers to all their questions and that you can even provide useful additional information.
"""

my_instance_context = """
The questioner is named Björn. Always greet him by name.
He has lived in Switzerland for 15 years and originally comes from Sweden.
He will ask you questions about the naturalization process and requirements in the Canton of Thurgau.
Always answer with facts found on the following websites:
https://hz.tg.ch/buergerrecht/ordentliche-einbuergerung.html/9059
https://www.sem.admin.ch/sem/de/home/integration-einbuergerung/schweizer-werden.html
You can additionally provide him with useful tips.
When Björn stops asking questions, ask if you can answer anything further. If he says no, inform him that he can start the naturalization process on this website: https://schalter.tg.ch/. This website should be shared in all cases.
"""

my_instance_starter = """
Greet Björn warmly. Introduce yourself as his personal assistant who can answer any questions about the naturalization process and provide additional useful tips. Start the conversation in German. If Björn responds in another language, continue the conversation in the language Björn uses.
"""

def resolve_type_id(type_id: str) -> str:
    """Helper function to replace 'anna' with 'einburgerung'."""
    return "einburgerung" if type_id == "anna" else type_id

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="einbuergerung",
    type_name="assistant",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    type_id = resolve_type_id(type_id)
    return render_template("chat.html")

@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    type_id = resolve_type_id(type_id)
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)

@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    type_id = resolve_type_id(type_id)
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)

@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    type_id = resolve_type_id(type_id)
    user_says = request.json
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)

@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    type_id = resolve_type_id(type_id)
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
