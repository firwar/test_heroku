import requests
import pickle
import json
import datetime
import csv
import json
import re
from flask import render_template, flash, redirect, jsonify
from app import app
from app.forms import LoginForm
from pyairtable import Table, Api

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Airtable'}
    return render_template('index.html', title='Home', user=user, environment=app.config['FLASK_ENV'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/run_script', methods=['POST'])
def simple_record_match():
    app.commonly_airtable.simple_record_match("Week1") 
    return jsonify({"message": "Task finished successfully!"})

@app.route('/advanced_match', methods=['POST'])
def advanced_match():
    app.commonly_airtable.delete_match_data()
    app.commonly_airtable.advanced_record_match("Week1") 
    return jsonify({"message": "Task finished successfully!"})



@app.route('/load_users', methods=['POST'])
def load_users():
    # app.commonly_airtable.delete_all_data()
    column_names = ''
    rows = ''
    # with open('db.txt', 'rb') as f:
    #     column_names, rows = pickle.load(f)

    # load from postgres
    column_names, rows = app.commonly_postgres.fetch_data_from_postgres()
    app.commonly_airtable.send_data_to_airtable(column_names, rows)
    return jsonify({"message": "Task finished successfully!"})


@app.route('/create_paperforms', methods=['POST'])
def create_paperforms():

    group_records = app.commonly_airtable.get_group_records()
    app.commonly_paperform.start_driver_login()
    i = 0
    updated_group_records = []
    for record in group_records:
        if record['fields']['status'] != 'confirmed':
            continue
        if record['fields'].get('paperform_link', None) != None:
            continue
        names = record['fields']['first_name']
        venue = record['fields']['venue_name'][0]
        print(venue)
        names_list = names.split("\n")
        print(names_list)
        form_name = record['fields']['Name']
        try:
            paperform_link = app.commonly_paperform.create_post_survey_form(form_name, names_list, venue)
            updated_group_records.append({'id': record['id'], 'fields': {"paperform_link": paperform_link}})
            app.commonly_airtable.update_group_records(updated_group_records)
            updated_group_records = []
        except Exception as e:
            print("Exception:", e)

        i = i+1
    app.commonly_paperform.close()

    return jsonify({"message": "Task finished successfully!"})

@app.route('/email_matches', methods=['POST'])
def email_matches():
    group_records = app.commonly_airtable.get_group_records() 
    records_emailed = []
    for record in group_records:
        if record['fields']['status'] == 'confirmed' and record['fields'].get('email_matched', None) == None and record['fields'].get('venue_name', None) != None:
            names = record['fields']['first_name'].split('\n')
            venue_name = record['fields']['venue_name'][0]
            venue_address = record['fields']['venue_address'][0]
            day = record['fields']['avail_day']
            if day == 'Tuesday':
                date = "Tuesday, 9/5"
                time = "7PM"
            elif day == 'Thursday':
                date = "Thursday, 9/7"
                time = "7PM"
            elif day == 'Sunday':
                date = "Sunday, 9/10"
                time = "12PM"
            group_size = record['fields']['attendees']
            emails = record['fields']['email'].split('\n')
            emails = ",".join(emails)
            groupme = record['fields'].get('groupme_link', " ")
            try:
                app.commonly_customerio.send_match_message(names, venue_name, venue_address, date, time, group_size, emails, groupme)
                records_emailed.append(record) 
            except Exception as e:
                print("failed to draft emails to matches")
                print(e)

        updated_records_emailed = [] 
        for i in range(len(records_emailed)):
            updated_records_emailed.append({'id': records_emailed[i]['id'], 'fields' : {"email_matched": True}})

        app.commonly_airtable.group_table.batch_update(updated_records_emailed)


    return jsonify({"message": "Task finished successfully!"})



@app.route('/reset_tables', methods=['POST'])
def reset_tables():
    app.commonly_airtable.delete_all_data()
    return jsonify({"message": "Task finished successfully!"})


@app.route('/process_surveys', methods=['POST'])
def process_surveys():
    all_records = app.commonly_airtable.get_all_records()
    group_records = app.commonly_airtable.get_group_records() 
    url = "https://api.paperform.co/v1/forms/yxvhytrn/submissions"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer [insert auth]"
    }

    response = requests.get(url, headers=headers)

    print(response.text)
    response_json = json.loads(response.text)
    submissions = response_json['results']['submissions']
    #try:
    print(submissions)

    for submission in submissions:
        key_list = list(submission["data"].keys())
        print(submission["data"][key_list[0]])
        user_email = submission["data"][key_list[0]]
        print(submission["data"][key_list[9]])
        # List of users
        print(submission["data"][key_list[9]][0])
        # index of selected users
        print(submission["data"][key_list[9]][1][1])
        match_index = submission["data"][key_list[9]][1][1]
        # Name of user
        print(submission["data"][key_list[9]][0][match_index])
        match_name = submission["data"][key_list[9]][0][match_index]

        #for records in all_records:
            #if (record['fields']['email'] == user_email):

        # need to do for each
        updated_week_records = []
        for record in group_records:
            first_names = record['fields']['first_name'].split('\n')
            emails = record['fields']['email'].split('\n')
            first_names_index = -1
            try:
                first_names_index = first_names.index(match_name)
            except:
                pass
            if (first_names_index == -1):
                continue
            match_email = emails[first_names_index]
            print("match_email")
            print(match_email)
            break
        user_record_index = None
        user_record_id = None
        match_record_index = None
        match_record_id = None
        for i in range(len(all_records)):
            if (all_records[i]['fields']['email'] == match_email):
                match_record_index = i
                match_record_id = all_records[i]['id']
            if (all_records[i]['fields']['email'] == user_email):
                user_record_index = i
                user_record_id = all_records[i]['id']

        print(user_record_index)
        print(match_record_index)
        print(match_record_id)
        if (match_record_index == None or user_record_index == None or match_record_id == None or user_record_id == None):
            print("Not found")
        else:
            matched_record_update = all_records[user_record_index]['fields'].get('matched_with', [])
            matched_record_update.append(match_record_id)
            updated_week_records.append({'id': user_record_id, 'fields': {'matched_with': matched_record_update}})

        app.commonly_airtable.update_all_records(updated_week_records)

        #print(submission["data"][9][0])
        #print(submission["data"][9][0][1])

    #except Exception as e:
    #    print(exception)
    #    print(e)
    return jsonify({"message": "Task finished successfully!"})

@app.route('/update_matched', methods=['POST'])
def update_matched():
    app.commonly_airtable.set_matched_users("Week1")
    return jsonify({"message": "Matched users updated!"})




 