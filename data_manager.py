import csv
import os
import database_common
from psycopg2 import sql


@database_common.connection_handler
def get_data(cursor, table):
    if table == 'question':
        query = """
            SELECT *
            FROM question
            """
    if table == 'answer':
        query = """
            SELECT *
            FROM answer
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def write_question(cursor, submission_time, view_number, vote_number, title, message, image):
    query = """
    INSERT INTO question (submission_time, view_number, vote_number, title, message, image) 
    VALUES (%s, %s, %s, %s, %s, %s);"""
    cursor.execute(query, (submission_time, view_number, vote_number, title, message, image))


@database_common.connection_handler
def write_comment(cursor):
    query = """
    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count) 
    VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(query, (question_id, answer_id, message, submission_time, edited_count))


@database_common.connection_handler
def write_answer(cursor, submission_time, vote_number, question_id, message, image):
    query = """
    INSERT INTO answer (submission_time, vote_number, question_id, message, image) 
    VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(query, (submission_time, vote_number, question_id, message, image))


@database_common.connection_handler
def write_tag(cursor):
    query = """
    INSERT INTO tag (submission_time, view_number, vote_number, title, message, image) 
    VALUES (%s, %s, %s, %s, %s, %s);"""
    cursor.execute(query, (submission_time, view_number, vote_number, title, message, image))


@database_common.connection_handler
def modify_question_vote(cursor, question_id, vote):
    query = """
        UPDATE question
        SET vote_number = vote_number + %(vote)s
        WHERE id = %(question_id)s;
        """
    cursor.execute(query, {"vote": vote, "question_id": question_id})


@database_common.connection_handler
def modify_answer_vote(cursor, vote, answer_id):
    query = """
        UPDATE answer
        SET vote_number = vote_number + %s
        WHERE id = %s;
        """
    cursor.execute(query, (vote, answer_id,))


@database_common.connection_handler
def delete_an_answer(cursor, answer_id):
    query = """
        DELETE from answer
        WHERE answer_id = %s;"""
    cursor.execute(query, (answer_id,))


@database_common.connection_handler
def delete_a_question(cursor, question_id):
    query1 = """
        DELETE from question
        WHERE id = %s;
        """
    query2 = """
            DELETE from question_tag
            WHERE question_id = %s;
            """
    query3 = """
            DELETE from comment
            WHERE question_id = %s;
            """
    cursor.execute(query3, (question_id,))
    cursor.execute(query2, (question_id,))
    cursor.execute(query1, (question_id,))


@database_common.connection_handler
def get_question_by_id(cursor, id):
    query = """
        SELECT *
        FROM question
        WHERE id = %(id)s
        """
    cursor.execute(query, {"id": id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_by_id(cursor, id):
    query = """
        SELECT *
        FROM answer
        WHERE id = %(id)s
        """
    cursor.execute(query, {"id": id})
    return cursor.fetchall()


@database_common.connection_handler
def modify_question(cursor,  title, message, image_path, question_id):
    query = """
            UPDATE question
            SET title, message, image_path = %s, %s, %s
            WHERE question_id = %s;"""
    cursor.execute(query, (title, message, image_path, question_id,))


@database_common.connection_handler
def sort_questions(cursor, sortby='submission_time', order='DESC'):
    if order == 'ASC':
        query = sql.SQL("SELECT title FROM question ORDER BY {sort_by} ASC ;")
    if order == 'DESC':
        query = sql.SQL("SELECT title FROM question ORDER BY {sort_by} DESC ;")
        cursor.execute(query.format(sort_by=sql.Identifier(sortby)))
    return cursor.fetchall()                                                    #ezzel segített Balázs, hogy ne kelljen
                                                                                #if-et vagy f-stringet használni



