from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from os import urandom
import data_manager
import password_util
from datetime import datetime
from functools import wraps
import bonus_questions


app = Flask(__name__)
# UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/images')
UPLOAD_FOLDER = '/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = urandom(24)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} #not compulsory to define extensions

# https://pythonprogramming.net/decorator-wrappers-flask-tutorial-login-required/
def login_required(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if 'id' in session:
            return function(*args, **kwargs)
        else:
            flash("You are not logged in")
            return redirect(url_for('login'))
    return wrap

def already_logged_in(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if 'id' not in session:
            return function(*args, **kwargs)
        else:
            flash(f"You are already logged in, {session['username']}")
            return redirect(url_for('list_questions'))
    return wrap


#Hanna
@app.route("/list")
@app.route("/", methods=['GET'])
def list_questions():
    if 'username' in session and password_util.verify_password(session['password'], password_util.hash_password(session['password'])) == True:
        session['logged_in'] = True
    else:
        session['logged_in'] = False
    question_all = data_manager.get_data('question')
    if request.args:
        sort_by = request.args['sort_by']
        order = request.args['order']
    else:
        sort_by = 'submission_time'
        order = 'DESC'
    questions = data_manager.sort_questions(sort_by, order)
    order_options = data_manager.ORDER_OPTIONS

    return render_template('index.html', questions=questions,
        sort_options=data_manager.SORTING_OPTIONS, sort_by=sort_by, order_options=order_options, order=order, all_questions=question_all)
#Hanna
#Berni
#new answer / post an answer
@app.route('/question/<question_id>/new-answer', methods = ['GET', 'POST'])
def new_answer(question_id):
    if request.method == "POST":
        user_id = session['id']
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        vote_number =str(0)
        question_id = question_id
        message = request.form.get("message")
        filename = ''
        if request.files.get('image').filename != "":
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = os.path.dirname(__file__) + app.config['UPLOAD_FOLDER'] + filename
            image.save(image_path)
        data_manager.write_answer(submission_time, vote_number, question_id, message, filename, user_id)
        return redirect("/question/" + str(question_id))
    return render_template("new_answer.html", question_id=question_id)


@app.route('/answer/<answer_id>/delete')
def delete_an_answer(answer_id):
    data_manager.delete_an_answer(answer_id)
    # return redirect("/question/" + str(question_id))
    return redirect("/")


@app.route('/question/<question_id>/delete')
def delete_a_question(question_id):
    data_manager.delete_a_question(int(question_id))
    return redirect("/")

#Berni
#Vero
@app.route("/question/<question_id>")
def display_question(question_id):
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_for_question(question_id)
    question_comments = data_manager.get_question_comments(question_id)
    for answer in answers:
        answer['comments'] = data_manager.get_answer_comments(answer['id'])
    tags = data_manager.get_question_tag(question_id)
    data_manager.increase_view(question_id)
    return render_template("display_question.html", question = question, answers = answers, question_comments = question_comments, tags = tags)


@app.route("/answer/<answer_id>/edit", methods=['POST', 'GET']) #ide mégis kéne a get is, hiszen gettel is élünk; lekérjük az url-t, az egy get hívás
def edit_answer(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    answer_id = answer_id
    question = data_manager.get_question_by_answer_id(answer_id)
    original_answer = answer['message']
    if request.method == "POST":
        new_message = request.form['message']
        filename = ''
        if request.files.get('image').filename != "":
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = os.path.dirname(__file__)+app.config['UPLOAD_FOLDER']+filename
            image.save(image_path)
            data_manager.edit_answer(new_message, answer_id, filename)
        return redirect(url_for('display_question', question_id=question['question_id']))
    else:

        return render_template("edit_answer.html", answer_id = answer_id, original_answer = original_answer) #ide redirect question/question<id> kéne, hogy amikor posttal beküldöd a formot, vigyen vissza a kérdéshez


@app.route("/question/<question_id>/edit", methods=["GET", "POST"]) #get amikor megjelenít, ha rányom a submit gombra, akkor Post
def edit_question(question_id):
    question=data_manager.get_question_by_id(question_id) #vedd ki a szükséges kérdést
    if request.method == 'POST': #ha rányom a submit-ra, akkor az új infót küldd el a d_m.py-nak
        new_title = request.form['title']
        new_message = request.form['message']
        filename = ''
        if request.files.get('image').filename != "":
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = os.path.dirname(__file__)+app.config['UPLOAD_FOLDER']+filename
            image.save(image_path)
        data_manager.modify_question(new_title, new_message, filename, question_id)  # ez írja át a question.csv-t
        return redirect(f'/question/{question_id}') #jelenítsd meg a frissült kérdést
    return render_template("edit_question.html", question_id=question_id,
                           current_title=question['title'],
                           current_message=question['message'])


@app.route("/question/<question_id>/new-comment", methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'POST':
        user_id = session['id']
        message = request.form['new-comment']
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_manager.write_comment(question_id, message, submission_time, user_id)
        return redirect(f'/question/{question_id}')
    return render_template('display_question.html', question_id=question_id)


@app.route("/answer/<answer_id>/new-comment", methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    question_id_dict = data_manager.get_question_by_answer_id(answer_id)
    question_id = question_id_dict['question_id']
    if request.method == "POST":
        user_id = session['id']
        message = request.form['new-comment']
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_manager.write_comment_to_answer(answer_id, message, submission_time, user_id)
        return redirect(f'/question/{question_id}')
    return render_template('display_question.html', question_id=question_id, answer_id=answer_id)


@app.route("/comment/<comment_id>/delete", methods=["POST", "GET"])
def delete_comment(comment_id):
    if request.method == "GET":
        question_id = data_manager.get_comment_by_question_id(comment_id)[0]['question_id']
        data_manager.delete_comment(comment_id)
        return redirect(f'/question/{question_id}')

#Vero
#Luti
@app.route("/comment/<comment_id>/edit", methods=["POST", "GET"])
def edit_comment(comment_id):
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    question_id = data_manager.get_comment_by_question_id(comment_id)[0]['question_id']
    original_comment = data_manager.get_comment(comment_id)
    if request.method == "POST":
        comment = request.form['edited_comment']
        data_manager.edit_comment(comment, submission_time, comment_id)
        return redirect(f"/question/{question_id}")
    return render_template('edit_comment.html', original_comment = original_comment, q_id=question_id, comment_id=comment_id)


@app.route("/all_questions", methods=["GET"])
def all_questions():
    if 'username' in session and password_util.verify_password(session['password'], password_util.hash_password(
        session['password'])) == True:
        session['logged_in'] = True
    else:
        session['logged_in'] = False
    question_all = data_manager.get_data('question')
    if request.args:
        sort_by = request.args['sort_by']
        order = request.args['order']
    else:
        sort_by = 'submission_time'
        order = 'DESC'
    questions = data_manager.all_questions(sort_by, order)
    order_options = data_manager.ORDER_OPTIONS

    return render_template('all_questions.html', questions=questions,
                           sort_options=data_manager.SORTING_OPTIONS, sort_by=sort_by, order_options=order_options,
                           order=order, all_questions=question_all)


@app.route("/add-question", methods=['POST', 'GET'])
def add_question():
    view_number = 0
    vote_number = 0
    if request.method == 'POST':
        user_id = session['id']
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        view_number = view_number
        vote_number = vote_number
        title = request.form['title']
        message= request.form['message']
        filename = ''
        if request.files.get('image').filename != "":
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = os.path.dirname(__file__) + app.config['UPLOAD_FOLDER'] + filename
            image.save(image_path)
        data_manager.write_question(submission_time, view_number, vote_number, title, message, filename, user_id)
        return redirect("/")
    return render_template('add-question.html', id=id, question=data_manager.get_data('question'))


@app.route('/answer-vote/<id>/<vote>', methods=['POST'])
def answer_vote(id, vote):
    increment = 1 if vote == 'vote_up' else -1
    data_manager.modify_answer_vote(increment, id)
    return redirect(url_for('gain_rep_answer', id=id, vote=vote))


@app.route('/question-vote/<id>/<vote>', methods=['POST'])
def question_vote(id, vote):
    increment = 1 if vote == 'vote_up' else -1
    data_manager.modify_question_vote(id, increment)
    return redirect(url_for('gain_rep_question', id=id, vote=vote))


@app.route("/search", methods=['GET'])
def search_question():
    search_phrase = request.args.get('question')
    found_phrase = data_manager.search_question(search_phrase)
    return render_template('search.html', result=found_phrase, search_phrase=search_phrase)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.args.get('username')
        password = request.args.get('password')
        hashed_password = password_util.hash_password(str(password))
        reg_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_manager.add_new_user(username, hashed_password, reg_date)
        return redirect(url_for('list_questions'))
# Luti


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def question_tags(question_id):
    tags = data_manager.get_tags()
    if request.method == 'POST':
        new_tag = request.form['question_tag']
        for tag in tags:
            if tag['name'] == new_tag:
                tag_id = tag['id']
                data_manager.write_tags(tag_id, question_id)
                return redirect(f"/question/{question_id}")
        data_manager.write_new_tag(new_tag)
        tags = data_manager.get_tags()
        for tag in tags:
            if tag['name'] == new_tag:
                tag_id = tag['id']
                data_manager.write_tags(tag_id, question_id)
        return redirect(f"/question/{question_id}")
    return render_template('add_tag.html', question_tags=tags, question_id=question_id)


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_question_tag(question_id, tag_id):
    data_manager.delete_tag(question_id, tag_id)
    return redirect(f"/question/{question_id}")

@app.route("/login")
@already_logged_in
def login_page():
    return render_template('login.html')


@app.route("/login", methods = ["POST"])
def login():
        email_input = request.form.get('email')
        password_input = request.form.get('password')
        user_details = data_manager.get_user_by_email(email_input)
        if not user_details: #ha nincs ilyen user
            flash("No such username")
            return redirect(url_for('login'))
        else:
            password_verified = password_util.verify_password(password_input, user_details['hashed_password'])
            if not password_verified: #ha nem oké a jelszó
                flash("Wrong username or password")
                return redirect(url_for('login'))
            else:
                session['id'] = user_details['user_id']
                session['username'] = user_details['username']
                session['password'] = user_details['hashed_password']
                return redirect(url_for('list_questions'))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out")
    return render_template('login.html')

@app.route("/users")
@login_required
def users():
    if 'username' in session:
        users = data_manager.get_users()
        return render_template('all_users.html', users=users)
    else:
        return redirect(url_for('list_questions'))


@app.route('/answer-rep/<id>/<vote>')
def gain_rep_answer(id, vote):
    answer = data_manager.get_answer_by_id(id)
    user = answer['user_id']
    question_id = answer['question_id']
    if vote == 'vote_up':
        increment = 10
    elif vote == 'vote_down':
        increment = -2
    elif vote == 'accepted':
        increment = 15
    data_manager.change_reputation(increment, user)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question-rep/<id>/<vote>')
def gain_rep_question(id, vote):
    question = data_manager.get_question_by_id(id)
    user = question['user_id']
    ['user_id']
    if vote == 'vote_up':
        increment = 5
    elif vote == 'vote_down':
        increment = -2
    data_manager.change_reputation(increment, user)
    return redirect('/')


@app.route('/tags')
def tags():
    tags = data_manager.get_tags_with_numbers()
    return render_template('tags.html', tags=tags)

@app.route('/user/<user_id>')
@login_required
def user_profile(user_id):
    user_data = data_manager.get_profile_details_by_id(user_id)
    questions = data_manager.get_infos_by_user(user_id, 'question')
    answers = data_manager.get_infos_by_user(user_id, 'answer')
    comments = data_manager.get_infos_by_user(user_id, 'comment')
    return render_template('user_profile.html',
                    user_data=user_data,
                    user_id=user_id,
                    questions=questions,
                    answers=answers,
                    comments=comments)


@app.route('/mark-answer/<answer_id>', methods=['POST'])
def mark_answer(answer_id):
    question = data_manager.get_question_by_answer_id(answer_id)
    question_id = question['question_id']
    data_manager.change_accepted_state(answer_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/bonus-questions')
def filter_bonus_questions():
    questions = bonus_questions.SAMPLE_QUESTIONS
    return render_template("bonus_questions.html", questions=questions)

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
    )
