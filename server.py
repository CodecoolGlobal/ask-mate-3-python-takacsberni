from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from os import urandom
import data_manager
import password_util
from datetime import datetime

app = Flask(__name__)
# UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/images')
UPLOAD_FOLDER = '/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = urandom(24)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} #not compulsory to define extensions


#Hanna
@app.route("/list")
@app.route("/", methods=['GET'])
def list_questions():
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
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        vote_number =str(0)
        question_id = question_id
        message = request.form.get("message")
        image = request.form.get("image")
        data_manager.write_answer(submission_time, vote_number, question_id, message, image)
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
    original_answer = answer['message']
    if request.method == "POST":
        new_message = request.form['message']
        filename = ""
        if 'image' in request.files:
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            data_manager.edit_answer(new_message, answer_id, image_path)
        return redirect("/")
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
        message = request.form['new-comment']
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_manager.write_comment(question_id, message, submission_time)
        return redirect(f'/question/{question_id}')
    return render_template('display_question.html', question_id=question_id)


@app.route("/answer/<answer_id>/new-comment", methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    question_id_dict = data_manager.get_question_by_answer_id(answer_id)
    question_id = question_id_dict['question_id']
    if request.method == "POST":
        message = request.form['new-comment']
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_manager.write_comment_to_answer(answer_id, message, submission_time)
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


@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html')


@app.route("/add-question", methods=['POST', 'GET'])
def add_question():
    view_number = 0
    vote_number = 0
    if request.method == 'POST':
        questions = data_manager.get_data('question')
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        view_number = view_number
        vote_number = vote_number
        title = request.form['title']
        message= request.form['message']
        image = vote_number
        data_manager.write_question(submission_time, view_number, vote_number, title, message, image)
        question_id = questions[-1]['id'] #itt -1, köv. sorban +1, mert csak így tudtuk összehozni azt, hogy utolsó ID-val rendelkezőt jelenítse meg
        return redirect("/")
    return render_template('add-question.html', id=id, question=data_manager.get_data('question'))


@app.route('/answer-vote/<id>/<vote>', methods=['POST'])
def answer_vote(id, vote):
    increment = 1 if vote == 'vote_up' else -1
    data_manager.modify_answer_vote(increment, id)
    return redirect('/')


@app.route('/question-vote/<id>/<vote>', methods=['POST'])
def question_vote(id, vote):
    increment = 1 if vote == 'vote_up' else -1
    data_manager.modify_question_vote(id, increment)
    return redirect('/')


@app.route("/search", methods=['GET'])
def search_question():
    search_phrase = request.args.get('question')
    found_phrase = data_manager.search_question(search_phrase)
    return render_template('search.html', result=found_phrase, search_phrase=search_phrase)
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

@app.route("/login", methods = ["POST", "GET"])
def login():
    #kelleni fog egy users tábla, ahova tesszük őket
    if request.method == "POST":
        email_input = request.form.get('email')
        password_input = request.form.get('password')
        user_details = data_manager.get_user_details(email_input)
        if not user_details: #ha nincs ilyen user
            flash("No such username")
        else:
            password_verified = password_util.verify_hashed_password(user_details['password'], email_input)
            if not password_verified: #ha nem oké a jelszó
                flash("Wrong username or password")
                return redirect(url_for('login'))
            else:
                session['id'] = user_details['id']
                session['username'] = user_details['username']
                return redirect(url_for('list_questions'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

    # There should be a page where I can list all the registered users with all their attributes.
@app.route("/users")
def users():
    if 'user' in session:
        users = data_manager.get_users()
        return render_template('all_users.html', users=users)
    else:
        return redirect(url_for('list_questions'))


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
