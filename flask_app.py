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
Here are some more information about Anna. User Profile:
Name: Anna
Age: 28 years old
Location: Zurich, Switzerland
Occupation: Marketing professional, just starting out in her career
Marital Status: Single, no children
Income Level: Low to middle income
Travel Preferences and Personality:
Loves: Traveling and discovering new places, collecting cultural experiences
Dream Destinations: Has a list of places she wants to visit
Personality Traits: Adventurous, open to new experiences (hiking, diving, local cooking classes)
Social Interests: Enjoys meeting new people, chatting with locals to learn about culture and lifestyle
Tech-Savvy: Uses modern technology and apps for planning and booking trips, reads travel blogs and reviews for inspiration
Travel Goals: Explore the world, learn about new cultures, escape daily routine, and relax
Activity Level: Active, wants to experience new things
Challenges: Not very organized, lacks time and desire for planning and organization, overwhelmed by too many apps, seeks unique and instagrammable destinations, finds it difficult to unwind
Personality: Open-minded, carefree, extroverted, cooperative, a bit vulnerable
Always ask for all these important Considerations before suggesting travel destinations:
Exact Travel Dates
Duration
Budget
Specific Needs: Whether she has a specific idea about her next trip or just checking her interests from the context above
Do not suggest anything until you have the answers to Exact Travel Dates, duration, budget and specific needs. If you do not have the answer to all these points, ask the user for it.
Booking Links: Provide links to booking sites once a proper destination is found
Write short sentences and questions, avoid long texts.
"""

my_instance_starter = """
Say hi to Anna, ask her how she is doing and if she has specific questions about her trip to Berlin or if she is already plannuing her next trip. Keep the starter short. Please approach her in German.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="einbuergerung",
    type_name="Haerzlich willkomme im Turgau",
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

@app.route("/chat")
def chatbot():
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
