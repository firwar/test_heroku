import requests
import pickle
import json
import datetime
import csv
import re
from flask import render_template, flash, redirect, jsonify
from app import app
from app.forms import LoginForm
from pyairtable import Table, Api

#AIRTABLE_BASE_ID = "appPrjUSEv6JdAeVJ"
#AIRTABLE_TABLE_NAME = "TestUsers"
#AIRTABLE_GROUP_TABLE_NAME = "TestGroups"
#
#api = Api(app.config['AIRTABLE_API_KEY'])
#table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
#group_table = api.table(AIRTABLE_BASE_ID, AIRTABLE_GROUP_TABLE_NAME)

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


    # all_records = []

    # all_records = table.all()

    # # Sort by age
    # for record in all_records:
    #     age = record['fields'].get('age', None)
    #     if age is not None and not isinstance(age, int):
    #         record['fields']['age'] = 0
    #         print(f"Problematic age value: {age}")
    # sorted_records = sorted(all_records, key=lambda x: x['fields'].get('age',0))

    # group_records = []

    # # Add matches to table    
    # for i in range(len(sorted_records)):
    #     if i % 5 == 0:
    #         group_records.append({'UserTableID':[]})

    #     group_records[-1]['UserTableID'].append(sorted_records[i]['id'])
    # response = group_table.batch_create(group_records)
    # return jsonify({"message": "Task finished successfully!"})

@app.route('/load_users', methods=['POST'])
def load_users():
    app.commonly_airtable.delete_all_data()
    column_names = ''
    rows = ''
    with open('db.txt', 'rb') as f:
        column_names, rows = pickle.load(f)

    # load from postgres
    #column_names, rows = app.commonly_postgres.fetch_data_from_postgres()
    app.commonly_airtable.send_data_to_airtable(column_names, rows)
    return jsonify({"message": "Task finished successfully!"})

    # def row_to_record(row):
    #     return {
    #         column_names[i]: (value.isoformat() if isinstance(value, (datetime.date, datetime.datetime)) else value)
    #         for i, value in enumerate(row)
    #     }

    # availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    # records = [row_to_record(row) for row in rows]
    # for i in range(len(records)):
    #     records[i].pop('id')
    #     records[i]['time_avail'] = ', '.join(records[i]['time_avail'])
    #     records[i]['Status'] = "unmatched"
    #     records[i]['Week1'] = "unmatched"
    #     records[i]['Week2'] = "unmatched"
    #     records[i]['Week3'] = "unmatched"
    #     records[i]['Week4'] = "unmatched"
    #     records[i]['email_reg'] = True
    #     records[i]['email_match'] = False
    #     records[i]['Availability'] = []
    #     for j in range(len(availability_arr)):
    #         rand_value = random.randint(0,4)
    #         if (rand_value == 0):
    #             records[i]['Availability'].append(availability_arr[j])

    # #print(records[0])
    # #input()
    # # Send records to Airtable (Note: pyairtable does automatic batching)
    # response = table.batch_create(records)

    # # Check for errors (you can adjust this based on your needs)
    # for record in response:
    #     if 'error' in record:
    #         print(f"Failed to insert record: {record}. Error: {record['error']}")

    # return jsonify({"message": "Task finished successfully!"})

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
    #app.commonly_airtable.delete_all_data()
    # commonly get match records
    # for each group
        # get names
        # send group number, venue, names, to paperform
    return jsonify({"message": "Task finished successfully!"})

    # all_records = group_table.all()
    # all_record_ids = [record['id'] for record in all_records]
    # group_table.batch_delete(all_record_ids)

    # all_records = table.all()
    # all_record_ids = [record['id'] for record in all_records]
    # table.batch_delete(all_record_ids)
    # return jsonify({"message": "Task finished successfully!"})

@app.route('/reset_tables', methods=['POST'])
def reset_tables():
    all_record_ids = [record['id'] for record in all_records]
    group_table.batch_delete(all_record_ids)

    all_records = table.all()
    all_record_ids = [record['id'] for record in all_records]
    table.batch_delete(all_record_ids)
    return jsonify({"message": "Task finished successfully!"})

@app.route('/update_matched', methods=['POST'])
def update_matched():
    app.commonly_airtable.set_matched_users("Week1")
    return jsonify({"message": "Matched users updated!"})

    # all_records = group_table.all()
    # all_record_ids = [record['id'] for record in all_records]
    # group_table.batch_delete(all_record_ids)

    # all_records = table.all()
    # all_record_ids = [record['id'] for record in all_records]
    # table.batch_delete(all_record_ids)
    # return jsonify({"message": "Task finished successfully!"})





 