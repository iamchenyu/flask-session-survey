from crypt import methods
from http.client import responses
from urllib import response
from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey, personality_quiz, surveys
from decouple import config


app = Flask(__name__)
app.config["SECRET_KEY"] = config("SECRET_KEY")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/surveys")
def show_homepage():
    return render_template("homepage.html")


@app.route("/sessions", methods=["POST"])
def set_sessions():
    survey_type = request.form["survey_type"]
    if session.get(survey_type):
        if len(session[survey_type]["answers"]) == session[survey_type]["ttl_questions"]:
            return redirect(f"/surveys/{survey_type}/thank-you")
    else:
        session[survey_type] = {
            "type": survey_type,
            "answers": [],
            "current_question": 0,
            "ttl_questions": len(surveys[survey_type].questions),
        }
        return redirect(f"/surveys/{survey_type}")


@app.route("/surveys/<survey_type>")
def show_question(survey_type):
    if len(session[survey_type]["answers"]) == session[survey_type]["ttl_questions"]:
        return redirect(f"/surveys/{survey_type}/thank-you")
    else:
        survey = surveys[survey_type]
        q_idx = session[survey_type]["current_question"]
        if len(session[survey_type]["answers"]) == q_idx:
            checked_value = ""
        elif len(session[survey_type]["answers"]) > q_idx:
            checked_value = session[survey_type]["answers"][q_idx]
        return render_template("question.html", value=checked_value, survey=survey, survey_type=survey_type)


@app.route("/surveys/<survey_type>", methods=["POST"])
def go_back(survey_type):
    session[survey_type]["current_question"] -= 1
    session.modified = True
    return redirect(f"/surveys/{survey_type}")


@app.route("/<survey_type>/answer", methods=["POST"])
def save_answer(survey_type):
    choice = request.form["choices"]
    comment = request.form.get("comment")
    if comment:
        choice = {"choice": choice, "comment": comment}
    q_idx = session[survey_type]["current_question"]
    if len(session[survey_type]["answers"]) == q_idx:
        session[survey_type]["answers"].append(choice)
        session.modified = True
    elif len(session[survey_type]["answers"]) > q_idx:
        session[survey_type]["answers"][q_idx] = choice
    session[survey_type]["current_question"] += 1
    flash("Your answer has been saved!", "success")
    return redirect(f"/surveys/{survey_type}")


@app.route("/surveys/<survey_type>/thank-you")
def show_thank_you(survey_type):
    survey = surveys[survey_type]
    return render_template("thank_you.html", survey=survey, survey_type=survey_type)
