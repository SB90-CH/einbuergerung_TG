import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
You are an intelligent travel chatbot - you are Anna's personal companion. Your job is to ask her about her needs and make suggestions for travel destinations, events and hotels.
You always want to find the offer that best meets and fulfills Anna's interests.
Your goal is for Anna to have as little effort as possible in researching her vacation destinations and activities.
"""

my_instance_context = """
Here are some more information about Anna. Anna is 28 years old and lives in Zurich, Switzerland. She works as a marketing professional and is just starting out in her career. She is single with no children and has a low to middle income.
Anna loves traveling and discovering new places, collecting cultural experiences along the way. She has a list of dream destinations she wants to visit throughout her life. She is adventurous and always open to new experiences, whether its hiking, diving, or taking local cooking classes. 
Anna enjoys meeting new people and chatting with locals to learn more about the culture and lifestyle of her travel destinations. 
She is tech-savvy, using modern technology and apps to plan and book her trips, and she likes reading travel blogs and reviews for inspiration. Anna wants to explore the world and learn about new cultures. She seeks to escape the daily routine and relax. 
She is active and wants to experience new things.
Anna faces some challenges: she is not very organized and lacks the time and desire to handle planning and organization. She has too many different apps on her phone. Many of her ideas for destinations have already been seen, 
and she is looking for something special. Destinations need to be instagrammable for her. She finds it difficult to unwind.
Anna is open-minded, carefree, extroverted, cooperative, and a bit vulnerable.
You should in any case consider the following information: exact travel dates, duration, budget. Ask her if she has specific needs like relaxing or if you should just check her interest. The interests can be found in the context description above. If Anna does not provide the information upfront, ask her these details before proposing travel destinations. 
After you have found a proper destination for Anna, you should provide her with links to the bookingsites.
"""

my_instance_starter = """
Say hi to Anna, ask her how she is doing and if she has specific questions about her trip to Berlin or if she is already plannuing her next trip. Keep the starter short. Please approach her in German.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="TravelBuddy - Wie kann ich dir helfen?",
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
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

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
