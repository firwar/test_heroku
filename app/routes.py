import requests
import pickle
import json
import datetime
import csv
import re
import random
from flask import render_template, flash, redirect, jsonify
from app import app
from app.forms import LoginForm
from pyairtable import Table, Api

AIRTABLE_BASE_ID = "appPrjUSEv6JdAeVJ"
AIRTABLE_TABLE_NAME = "TestUsers"
AIRTABLE_GROUP_TABLE_NAME = "TestGroups"

api = Api(app.config['AIRTABLE_API_KEY'])
table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
group_table = api.table(AIRTABLE_BASE_ID, AIRTABLE_GROUP_TABLE_NAME)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Airtable'}
    return render_template('index.html', title='Home', user=user)

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
    all_records = []

    all_records = table.all()

    # Sort by age
    for record in all_records:
        age = record['fields'].get('age', None)
        if age is not None and not isinstance(age, int):
            record['fields']['age'] = 0
            print(f"Problematic age value: {age}")
    sorted_records = sorted(all_records, key=lambda x: x['fields'].get('age',0))

    group_records = []

    # Add matches to table    
    for i in range(len(sorted_records)):
        if i % 5 == 0:
            group_records.append({'UserTableID':[]})

        group_records[-1]['UserTableID'].append(sorted_records[i]['id'])
    response = group_table.batch_create(group_records)
    return jsonify({"message": "Task finished successfully!"})

@app.route('/load_users', methods=['POST'])
def load_users():
    reset_tables()
    column_names = ''
    rows = ''
    with open('db.txt', 'rb') as f:
        column_names, rows = pickle.load(f)


    def row_to_record(row):
        return {
            column_names[i]: (value.isoformat() if isinstance(value, (datetime.date, datetime.datetime)) else value)
            for i, value in enumerate(row)
        }

    availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    records = [row_to_record(row) for row in rows]
    for i in range(len(records)):
        records[i].pop('id')
        records[i]['time_avail'] = ', '.join(records[i]['time_avail'])
        records[i]['Status'] = "unmatched"
        records[i]['Week1'] = "unmatched"
        records[i]['Week2'] = "unmatched"
        records[i]['Week3'] = "unmatched"
        records[i]['Week4'] = "unmatched"
        records[i]['email_reg'] = True
        records[i]['email_match'] = False
        records[i]['Availability'] = []
        for j in range(len(availability_arr)):
            rand_value = random.randint(0,4)
            if (rand_value == 0):
                records[i]['Availability'].append(availability_arr[j])

    #print(records[0])
    #input()
    # Send records to Airtable (Note: pyairtable does automatic batching)
    response = table.batch_create(records)

    # Check for errors (you can adjust this based on your needs)
    for record in response:
        if 'error' in record:
            print(f"Failed to insert record: {record}. Error: {record['error']}")

    return jsonify({"message": "Task finished successfully!"})

@app.route('/reset_tables', methods=['POST'])
def reset_tables():
    all_records = group_table.all()
    all_record_ids = [record['id'] for record in all_records]
    group_table.batch_delete(all_record_ids)

    all_records = table.all()
    all_record_ids = [record['id'] for record in all_records]
    table.batch_delete(all_record_ids)
    return jsonify({"message": "Task finished successfully!"})



 