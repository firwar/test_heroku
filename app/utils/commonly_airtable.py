import requests
import copy
import pickle
import json
import datetime as dt
from datetime import datetime
import random
import csv
import re
import os
import math
import pytz
#from sklearn.metrics import pairwise_distances
#from scipy.spatial.distance import cosine
# import spacy
from pyairtable import Table, Api
from dotenv import load_dotenv
 
class CommonlyAirtable():
    
    def __init__(self, api_key, environment):

        if environment == "development":
            self.AIRTABLE_BASE_ID = "appVpcavXi3V5Mcou"
            self.AIRTABLE_TABLE_NAME = "Users"
            self.AIRTABLE_GROUP_TABLE_NAME = "Week1"

        if environment == "production":
            self.AIRTABLE_BASE_ID = "appzACnuRf6rWCDKJ"
            self.AIRTABLE_TABLE_NAME = "Users"
            self.AIRTABLE_GROUP_TABLE_NAME = "Week1"


        self.availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.api = Api(api_key)
        self.table = self.api.table(self.AIRTABLE_BASE_ID, self.AIRTABLE_TABLE_NAME)
        self.group_table = self.api.table(self.AIRTABLE_BASE_ID, self.AIRTABLE_GROUP_TABLE_NAME)
        # self.nlp = spacy.load("en_core_web_md")

    def dump_to_csv(self, column_names, rows, filename='output.csv'):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write the header
            writer.writerow(column_names)
            
            # Write the rows
            for row in rows:
                writer.writerow(row)


    def mock_data_to_airtable(self, column_names, rows):
        # Function to convert individual row to Airtable record format
        def row_to_record(row):
            return {
                column_names[i]: (value.isoformat() if isinstance(value, (dt.date, dt.datetime)) else value)
                for i, value in enumerate(row)
            }


        start_date_str = "2023-04-02 00:00:00"
        end_date_str = "2023-09-08 23:59:59"

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")


        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        records = [row_to_record(row) for row in rows]
        
        for i in range(len(records)):
            week_dates_avail = []
            records[i].pop('id')
            for date_string in records[i]['time_avail']:
                date_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                if start_date <= date_object <= end_date:
                    day_of_week = date_object.strftime('%A')
                    week_dates_avail.append(day_of_week)

            records[i]['time_avail'] = ', '.join(records[i]['time_avail'])
            records[i]['Week1'] = "unmatched"
            records[i]['Week2'] = "unmatched"
            records[i]['Week3'] = "unmatched"
            records[i]['Week4'] = "unmatched"
            records[i]['email_reg'] = True
            records[i]['email_match'] = False
            records[i]['Availability'] = []

            # Use actual computed avail
            #records[i]['Availability'] = week_dates_avail[:]

            # Use random computed avail
            for j in range(len(availability_arr)):
                rand_value = random.randint(0,2)
                if (rand_value == 0):
                    records[i]['Availability'].append(availability_arr[j])
            
            if len(records[i]['Availability']) == 0:
                rand_value = random.randint(0,4)
                records[i]['Availability'].append(availability_arr[rand_value])


        print("done")
        #print(records[0])
        #input()
        # Send records to Airtable (Note: pyairtable does automatic batching)
        response = self.table.batch_create(records)

        # Check for errors (you can adjust this based on your needs)
        for record in response:
            if 'error' in record:
                print(f"Failed to insert record: {record}. Error: {record['error']}")



    def send_data_to_airtable(self, column_names, rows):
        # Function to convert individual row to Airtable record format
        def row_to_record(row):
            return {
                column_names[i]: (value.isoformat() if isinstance(value, (dt.date, dt.datetime)) else value)
                for i, value in enumerate(row)
            }

        existing_records = self.get_all_records()
        existing_postgres_id_record_id = {}
        date_object_list = []
        # exiting postgres records
        for record in existing_records:
            date_string = record['fields']['avail_updated_at']
            date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
            date_object_list.append(date_object)
            existing_postgres_id_record_id[record['fields']['postgres_id']] = record['id']
        
        if (len(date_object_list) != 0):
            latest_updated_at = max(date_object_list)
        else:
            initial_date = "2020-08-26T17:38:38.364Z"
            latest_updated_at = datetime.strptime(initial_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # if id exists
        # check against available times
        # update available times if there is an update

        # start_date_str = "2023-04-02 00:00:00"
        # end_date_str = "2023-09-08 23:59:59"

        # start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        # end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")

        # records parsed from postgres
        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        records = [row_to_record(row) for row in rows]
        mountain_timezone = pytz.timezone('America/Denver') 
        records_to_update = []
        records_to_add = []
        for i in range(len(records)):
            week_dates_avail = []

            # Only process entries that have been last updated
            date_string = records[i]['avail_updated_at']
            print(date_string)
            updated_at = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
            updated_at = updated_at.replace(microsecond=0)
            if updated_at <= latest_updated_at:
                continue
            print("updates")
            print(updated_at)
            print(latest_updated_at)
            print("done")
            postgres_id = records[i].pop('id')
            for date_string in records[i]['time_avail']:
                date_object_utc = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                date_object_utc = pytz.utc.localize(date_object_utc)  # Marking as UTC

                # Convert to Mountain Time
                date_object_mt = date_object_utc.astimezone(mountain_timezone)
                day_of_week = date_object_mt.strftime('%A')
                week_dates_avail.append(day_of_week)

            records[i]['postgres_id'] = postgres_id
            records[i]['time_avail'] = ', '.join(records[i]['time_avail'])
            records[i]['Week1'] = "unmatched"
            records[i]['Week2'] = "unmatched"
            records[i]['Week3'] = "unmatched"
            records[i]['Week4'] = "unmatched"
            records[i]['email_reg'] = True
            records[i]['email_match'] = False
            records[i]['Availability'] = []

            # Use actual computed avail
            records[i]['Availability'] = week_dates_avail[:]
            if records[i]['postgres_id'] in existing_postgres_id_record_id:
                records_to_update.append(records[i])
            else:
                records_to_add.append(records[i])

            # Use random computed avail
            # for j in range(len(availability_arr)):
            #     rand_value = random.randint(0,2)
            #     if (rand_value == 0):
            #         records[i]['Availability'].append(availability_arr[j])
            
            # if len(records[i]['Availability']) == 0:
            #     rand_value = random.randint(0,4)
            #     records[i]['Availability'].append(availability_arr[rand_value])

        updated_records = []
        print(existing_postgres_id_record_id)
        for record in records_to_update:
            # record id 
            print(record['postgres_id'])
            print(existing_postgres_id_record_id[record['postgres_id']])
            updated_records.append({'id': existing_postgres_id_record_id[record['postgres_id']], 'fields': {'avail_updated_at': record['avail_updated_at'], 'time_avail': record['time_avail']}})
        print("to update")
        print(updated_records)

        self.table.batch_update(updated_records)

        print("to add")
        print(records_to_add)
        #print(records[0])
        #input()
        # Send records to Airtable (Note: pyairtable does automatic batching)
        response = self.table.batch_create(records_to_add)

        # Check for errors (you can adjust this based on your needs)
        for record in response:
            if 'error' in record:
                print(f"Failed to insert record: {record}. Error: {record['error']}")

    def delete_match_data(self):
        all_records = self.group_table.all()
        all_record_ids = [record['id'] for record in all_records]

        self.group_table.batch_delete(all_record_ids)


    def delete_all_data(self):

        all_records = self.group_table.all()
        all_record_ids = [record['id'] for record in all_records]
        self.group_table.batch_delete(all_record_ids)

        all_records = self.table.all()
        all_record_ids = [record['id'] for record in all_records]
        self.table.batch_delete(all_record_ids)


    def fetch_all(self):
        all_records = self.table.all()
        with open('records.txt','wb') as f:
            pickle.dump(all_records,f)

    def list_embedding(self,interest_list):
        # Average the vectors of words in the list
        # return sum([self.nlp(word).vector for word in interest_list]) / len(interest_list)
        pass

    def process_records(self):
        all_records = []
        with open('records.txt','rb') as f:
            all_records = pickle.load(f)

        interests = []
        for record in all_records:
            interest = record['fields']['interests']
            interest = re.sub(r'[^A-Za-z ,]+', ' ',str(interest))
            interest = interest.split(',')
            interests.append(interest)

        for interest in interests:
            print(interest)
        embeddings = [self.list_embedding(interest) for interest in interests]
        distance_matrix = pairwise_distances(embeddings, metric=cosine)

        # Sort by conceptual similarity (for demonstration purposes, we'll just sort the first list relative to others)
        reference_idx = 0
        sorted_indices = list(range(len(interests)))
        sorted_indices.sort(key=lambda x: distance_matrix[reference_idx][x])

        print("")
        print("")
        print("")
        sorted_interests = [interests[i] for i in sorted_indices]
        for interest in sorted_interests:
            print(interest)

    def simple_record_match(self, week_col_string):
        all_records = []

        all_records = self.table.all()

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
            # Create group matches of 5 based on age
            if i % 5 == 0:
                group_row_name = "Group" + str(i // 5)
                group_records.append({'Name': group_row_name, 'UserTableID':[]})

            # Add records to group
            group_records[-1]['UserTableID'].append(sorted_records[i]['id'])
        response = self.group_table.batch_create(group_records)

        # Now update from unmmatched
        updated_week_records = []
        for record in all_records:
            updated_week_records.append({'id': record['id'], 'fields': {week_col_string: 'proposed'}})

        self.table.batch_update(updated_week_records)

    def set_matched_users(self, week_col_string):
        all_records = self.table.all()
        group_records = self.group_table.all()

        matched_users_list = []
        for record in group_records:
            if 'status' in record['fields'] and record['fields']['status'] == 'confirmed':
                matched_users_list.extend(record['fields']['UserTableID'])
        updated_user_statuses = [] 
        for i in range(len(matched_users_list)):
            updated_user_statuses.append({'id': matched_users_list[i], 'fields' : {week_col_string: "confirmed"}})

        print(matched_users_list)
        self.table.batch_update(updated_user_statuses)

    def advanced_record_match(self, week_col_string):
        #random.seed(7)
        initial_temperature = 1000
        cooling_rate = 0.995
        num_iterations = 20000
        best_solution, best_overflow = self.simulated_annealing(initial_temperature, cooling_rate, num_iterations)

        group_records = []
        for i in range(len(best_solution)):
            group_row_name = "Group" + str(i)
            group_records.append({'Name': group_row_name, 'UserTableID':[]})
            availability_string = "None"
            for j in range(len(self.availability_arr)):
                availability_found = True
                for k in range(len(best_solution[i])):
                    if self.availability_arr[j] not in best_solution[i][k]['fields']['Availability']:
                        availability_found = False
                        break
                if availability_found == False:
                    continue
                else:
                    availability_string = self.availability_arr[j]
                    break

            for j in range(len(best_solution[i])):
                group_records[-1]['UserTableID'].append(best_solution[i][j]['id'])
                group_records[-1]['avail_day'] = availability_string


        response = self.group_table.batch_create(group_records)

        # Now update from unmmatched
        updated_week_records = []
        for records in best_solution:
            for record in records:
                updated_week_records.append({'id': record['id'], 'fields': {week_col_string: 'proposed'}})
        for record in best_overflow:
            updated_week_records.append({'id': record['id'], 'fields': {week_col_string: 'unmatched'}})
        for records in best_solution: 
            for record in records:
                print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])
            print("\n")

        print("Overflow")
        for record in best_overflow:
            print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])
        print("\n")
    
        self.table.batch_update(updated_week_records)

    def simulated_annealing(self, initial_temperature, cooling_rate, num_iterations):
        #current_solution = generate_initial_solution(people)
        [current_solution, current_overflow] = self.get_initial_solution()
        current_energy = self.get_energy(current_solution, current_overflow)
        print("current energy: " + str(current_energy)) 
        best_solution = current_solution
        best_overflow = current_overflow
        best_energy = current_energy

        T = initial_temperature
        current_energy_last = 0
        stuck_count = 0
        for i in range(num_iterations):
            neighbor = []
            neighbor_overflow = []
            num_swaps = random.randint(1, 1)
            for _ in range(num_swaps):
                neighbor, neighbor_overflow = self.generate_neighbor(current_solution, current_overflow)
            neighbor_energy = self.get_energy(neighbor, neighbor_overflow)
            if (current_energy_last == current_energy):
                stuck_count +=1
                #print(stuck_count)
            else:
                stuck_count = 0

            current_energy_last = current_energy 
            if (stuck_count > 10000):
                print("THIS IS STUCK")
                T = initial_temperature
                stuck_count = 0
                pass
            if (neighbor_energy >= 10000000):
                continue
            print(str(i) + " neighbor_energy: " + str(current_energy))
            
            #potentially
            if neighbor_energy < current_energy:
                current_solution, current_energy, current_overflow = neighbor, neighbor_energy, neighbor_overflow
            else:
                delta = neighbor_energy - current_energy
                probability = math.exp(-delta / T)
                
                if random.random() < probability:
                    current_solution, current_energy, current_overflow = neighbor, neighbor_energy, neighbor_overflow
            
            if current_energy < best_energy:
                best_solution, best_energy, best_overflow = current_solution, current_energy, current_overflow

            T *= cooling_rate


        return best_solution, best_overflow


    # groups
    # [ [records1, record2, record3, record4 ]  , [  ]] 
    # [ records1. availabilities]
    def get_energy(self, groups, overflow_list):
        def get_amplification_factor(age):
            if 0 <= age < 25:
                return 80
            elif 25 <= age < 30:
                return 40
            elif 30 <= age < 35:
                return 20
            elif 35 <= age < 45:
                return 10
            elif 45 <= age < 55:
                return 5

            else:
                return 1  # default factor for ages not specified above        

        def get_amplification_factor_age(min_age, max_age):
            if min_age < 23 and max_age > 35:
                return 10000000
            elif min_age < 30 and max_age > 39:
                return 10000000

            else:
                return 1  # default factor for ages not specified above        



        calculated_energy = 10000000
        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i in range(len(groups)):
            outer_availability_found = False
            #for j in range(len(groups[i])):
            #    print(groups[i][j]['fields']['first_name'])
            for j in range(len(availability_arr)):

                # compare with every record in group
                availability_found = True
                for k in range(len(groups[i])):
                    # i.e. if Monday not in records availability
                    if availability_arr[j] not in groups[i][k]['fields']['Availability']:
                        availability_found = False
                        break
                # 
                if availability_found == False:
                    continue
                else:
                    outer_availability_found = True
                    break
            if (outer_availability_found == False):
                calculated_energy = 10000000
                return calculated_energy
        for i in range(len(groups)):
            if len(groups[i]) > 7 or len(groups[i]) < 4:
                calculated_energy = 10000000
                return calculated_energy

        # have a calculation at the end for how well each group matches
        A = 1000
        B = 5
        variance_total = 0
        age_list = []
        for i in range(len(groups)):
            age_list = []
            for j in range(len(groups[i])):
                age = groups[i][j]['fields'].get('age', None)
                age_list.append(age)
                if age is not None and not isinstance(age, int):
                    #record['fields']['age'] = 0
                    print(f"Problematic age value: {age}")
            #if (i == 4 or i == 18):
            #    print(age_list)
            mean = sum(age_list) / len(age_list)
            #print("mean: " + str(i) + ": " + str(mean))
            variance = sum((x - mean) ** 2 for x in age_list) / len(age_list)
            #print("vari: " + str(i) + ": " + str(variance))

            variance_total += variance * (get_amplification_factor(min(age_list)))*10

        calculated_energy = variance_total


        closeness_energy = 0
        for i in range(len(groups)):
            friendly_location_arr = []
            for j in range(len(groups[i])):
                friendly_location_arr.append(groups[i][j]['fields']['friendly_location'])
            closeness = self.closeness_score(friendly_location_arr) * 100
            closeness_energy += closeness
            
        calculated_energy += closeness_energy


        min_group_energy = 0
        for i in range(len(groups)):
            if(len(groups[i]) <= 4):
                min_group_energy += 3000
            elif(len(groups[i]) <= 5):
                min_group_energy += 1000
            elif(len(groups[i]) >= 7):
                min_group_energy += 1000

        calculated_energy += min_group_energy

        calculated_energy += len(overflow_list) * len(overflow_list) * 500

        return calculated_energy 
    # neighbor algorith
    # swap two people 
    # move one to different group


    def generate_neighbor(self, input_group, overflow):
        groups = copy.deepcopy(input_group)
        overflow_list = copy.deepcopy(overflow)

        def get_age_bracket(age):
            if 0 <= age < 25:
                return 2
            elif 25 <= age < 30:
                return 3
            elif 30 <= age < 35:
                return 4
            elif 35 <= age < 45:
                return 5
            elif 45 <= age < 55:
                return 6
            else:
                return 7


        # Create a new solution by swapping two random people between groups,
        # moving a person from one group to another, or other random changes.
        rand_value = random.randint(0,10)
        #if rand_value == 7:
        #    rand_value = random.randint(1,10)
        if rand_value > 8:
            rand_value = 6
        # add overflow to group
        if rand_value == 1 and len(overflow_list) > 0:
            rand_first_index = random.randint(0, len(groups)-1)
            rand_overflow_index = random.randint(0, len(overflow_list)-1)

            groups[rand_first_index].append(overflow_list[rand_overflow_index])
            overflow_list.pop(rand_overflow_index)

        # swap group member with overflow member
        elif rand_value == 2 and len(overflow_list) > 0:
            rand_first_index = random.randint(0, len(groups)-1)
            random_first_group_index = random.randint(0,len(groups[rand_first_index])-1)

            rand_overflow_index = random.randint(0, len(overflow_list)-1)
            #print(groups[rand_first_index][random_first_group_index]['fields']['first_name'])
            #print(groups[rand_second_index][random_second_group_index]['fields']['first_name'])
            #print(rand_first_index)
            #print(rand_second_index)
            temp_record = groups[rand_first_index][random_first_group_index]
            groups[rand_first_index][random_first_group_index] = overflow_list[rand_overflow_index]
            overflow_list[rand_overflow_index] = temp_record
        # remove group member from one group and add to other group
        # todo: may need to copy this
        elif rand_value == 3:
            rand_first_index = random.randint(0, len(groups)-1)
            rand_second_index = random.randint(0, len(groups)-1)
            while (rand_second_index == rand_first_index):
                rand_second_index = random.randint(0, len(groups)-1)

            random_first_group_index = random.randint(0,len(groups[rand_first_index])-1)

            temp_record = groups[rand_first_index][random_first_group_index]
            groups[rand_first_index].pop(random_first_group_index)
            groups[rand_second_index].append(temp_record)
        # remove group member add to overflow
        # elif rand_value == 4:
        #     rand_first_index = random.randint(0, len(groups)-1)
        #     random_first_group_index = random.randint(0,len(groups[rand_first_index])-1)

        #     temp_record = groups[rand_first_index][random_first_group_index]
        #     groups[rand_first_index].pop(random_first_group_index)
        #     overflow_list.append(temp_record)

        elif rand_value == 4:
            rand_first_index = random.randint(0, len(groups) - 1)
            rand_first_index = 0 
            # Identify the member with the lowest or highest age
            # For lowest age
            min_age_member = min(groups[rand_first_index], key=lambda x: x['fields']['age'])
            # For highest age
            max_age_member = max(groups[rand_first_index], key=lambda x: x['fields']['age'])


            rand_high_low = random.randint(0,1)
            # Remove the identified member from the group
            if rand_high_low == 0:
                overflow_list.append(min_age_member)  # Use max_age_member for highest age
                groups[rand_first_index].remove(min_age_member)  # Use max_age_member for highest age
                #print(min_age_member)
            else:
                overflow_list.append(max_age_member)  # Use max_age_member for highest age
                groups[rand_first_index].remove(max_age_member)  # Use max_age_member for highest age


            # Add the removed member to the overflow list

        elif rand_value == 5:  # Cluster users of same age bracket
            rand_group_index = random.randint(0, len(groups)-1)
            age_brackets = [get_age_bracket(member['fields']['age']) for member in groups[rand_group_index]]
            common_bracket = max(set(age_brackets), key=age_brackets.count)

            for i, group in enumerate(groups):
                if i != rand_group_index:
                    for j, member in enumerate(group):
                        if get_age_bracket(member['fields']['age']) == common_bracket:
                            # Swap this member with a random member of the chosen group
                            rand_member_index = random.randint(0, len(groups[rand_group_index])-1)
                            group[j], groups[rand_group_index][rand_member_index] = groups[rand_group_index][rand_member_index], group[j]
                            break

        elif rand_value == 6:  # Swap users based on age differences
            rand_group_index = random.randint(0, len(groups)-1)
            mean_age = sum(member['fields']['age'] for member in groups[rand_group_index]) / len(groups[rand_group_index])
            furthest_member = max(groups[rand_group_index], key=lambda x: abs(x['fields']['age'] - mean_age))

            # Find another group and member that would minimize the age variance if swapped in
            best_swap = None
            best_variance = float('inf')

            for i, group in enumerate(groups):
                if i != rand_group_index:
                    for j, member in enumerate(group):
                        temp_group = groups[rand_group_index].copy()
                        temp_group.remove(furthest_member)
                        temp_group.append(member)
                        temp_mean = sum(m['fields']['age'] for m in temp_group) / len(temp_group)
                        variance = sum((x['fields']['age'] - temp_mean) ** 2 for x in temp_group)

                        if variance < best_variance:
                            best_variance = variance
                            best_swap = (i, j)

            if best_swap:
                i, j = best_swap
                groups[rand_group_index].remove(furthest_member)
                groups[rand_group_index].append(groups[i][j])
                groups[i][j] = furthest_member

        elif rand_value == 7:
            # Find the group with the smallest size
            smallest_group_size = min(len(group) for group in groups)
            smallest_groups_indices = [i for i, group in enumerate(groups) if len(group) == smallest_group_size]
            
            # Select one of the smallest groups randomly for disbanding
            disband_group_index = random.choice(smallest_groups_indices)
            disbanded_members = groups[disband_group_index][:]  # Make a copy of the group members
            
            # Empty the disbanded group
            groups[disband_group_index] = []
            
            # Now, we need to distribute the members of the disbanded group to other groups
            # We'll shuffle the groups to distribute members randomly
            other_group_indices = [i for i in range(len(groups)) if i != disband_group_index]
            random.shuffle(other_group_indices)

            for member in disbanded_members:
                for group_index in other_group_indices:
                    if len(groups[group_index]) < 7:  # Ensure the group can accommodate more members
                        groups[group_index].append(member)
                        break

        # elif rand_value == 8:
        #     group_len = []
        #     group_index = []
        #     for i in range(len(groups)):
        #         group_len.append(len(groups[i]))
        #         group_index.append(i)
        #     groups_len_sorted, groups_index_sorted = zip(*sorted(zip(group_len, group_index)))

        #     # len of all groups in order
        #     print(groups_index_sorted)

        #     # the number of items in index 0
        #     second_index_list = []
        #     for i in range(len(groups[groups_index_sorted[0]])):
        #         second_index_list.append(i)

        #     random.shuffle(second_index_list)

        #     for i in range(len(groups[groups_index_sorted[0]])):
        #         value = groups[groups_index_sorted[0]].pop()
        #         groups[groups_index_sorted[1 + second_index_list[i]]].append(value)

        # swap two group members
        else:
            rand_first_index = random.randint(0, len(groups)-1)
            rand_second_index = random.randint(0, len(groups)-1)
            while (rand_second_index == rand_first_index):
                rand_second_index = random.randint(0, len(groups)-1)

            random_first_group_index = random.randint(0,len(groups[rand_first_index])-1)
            random_second_group_index = random.randint(0,len(groups[rand_second_index])-1)

            #print(groups[rand_first_index][random_first_group_index]['fields']['first_name'])
            #print(groups[rand_second_index][random_second_group_index]['fields']['first_name'])
            #print(rand_first_index)
            #print(rand_second_index)
            temp_record = groups[rand_first_index][random_first_group_index]
            groups[rand_first_index][random_first_group_index] = groups[rand_second_index][random_second_group_index]
            groups[rand_second_index][random_second_group_index] = temp_record


 
            #print(groups[rand_first_index][random_second_group_index]['fields']['first_name'])
            #print(groups[rand_second_index][random_first_group_index]['fields']['first_name'])

        # ... (implement the logic to generate a neighboring solution)
        # print("")
        # for records in groups: 
        #     for record in records:
        #         print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'] + " " + record['fields']['first_name'])

        #     print("")

        # print("overflow")
        # for record in overflow_list:
        #     print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'] + " " + record['fields']['first_name'])
        #     #print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])


        return groups, overflow_list

    def get_initial_solution(self):
        all_records = []

        all_records = self.table.all()

        friendly_location_circle = ['NW','N','NE','E','SE','S','SW','W']
        friendly_location = {}
    # id
    # availability
    # age
    # location    
        # Sort by age
        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        availability_count = [0, 0, 0, 0, 0, 0, 0]
        #all_records = list(filter(lambda record: record['fields'].get('friendly_location',None) != None and record['fields']['friendly_location'] != 'Out of Range', all_records))
        all_records = list(filter(lambda record: record['fields'].get('active',None) != None and record['fields'].get('supported', None)!=None, all_records))
        for record in all_records:
            record['fields']['processed'] = False
            for day in record['fields']['Availability']:
                availability_count[availability_arr.index(day)] += 1
            print(availability_count)

        print(availability_count)
        list1, list2 = zip(*sorted(zip(availability_count, availability_arr)))
        print(list1)
        print(list2)
        availability_sorted = list(list2)
        print(availability_sorted)
        # group_records = []
        # for day in availability_sorted:
        #     i = 0
        #     for j in range(len(all_records)):
        #         if record[j]['fields']['processed'] == False:
        #             if day in record[j]['fields']['Availability']:
        #                 if i % 5 == 0:
        #                     group_records.append([])
        #                 i += 1
        #                 group_records[-1].append(record)
        #                 record[j]['fields']['processed'] = True
        #                 record[j]['fields']['day'] = day

        group_records = []
        days_list = []
        overflow_list = []
        

        for day in availability_sorted:
            for record in all_records:
                if not record['fields']['processed'] and day in record['fields']['Availability']:
                    days_list.append(record)
                    record['fields']['processed'] = True
                    record['fields']['day'] = day

                    # Whenever we reach a group of 5, we add to group_records
                    if len(days_list) == 5:
                        group_records.append(days_list)
                        days_list = []
            if len(days_list) > 4:
                group_records.append(days_list)
            elif len(days_list) > 0:
                overflow_list.extend(days_list)
            
            days_list = []

        print(len(group_records))
        for records in group_records: 
            for record in records:
                print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'] + " " + record['fields']['first_name'])

            print("")

        print("overflow")
        for record in overflow_list:
            print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'] + " " + record['fields']['first_name'])
            #print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])



        #group_records[-1][-1]['fields']['Availability'] = ['Saturday']
        #energy = self.get_energy(group_records)
        #print(energy)
        #self.generate_neighbor(group_records)
        return group_records, overflow_list

        # for record in all_records:
        #     print(record)
        #     age = record['fields'].get('age', None)
        #     if age is not None and not isinstance(age, int):
        #         record['fields']['age'] = 0
        #         print(f"Problematic age value: {age}")
        # sorted_records = sorted(all_records, key=lambda x: x['fields'].get('age',0))

        # group_records = []

        # # Add matches to table    
        # for i in range(len(sorted_records)):
        #     # Create group matches of 5 based on age
        #     if i % 5 == 0:
        #         group_row_name = "Group" + str(i // 5)
        #         group_records.append({'Name': group_row_name, 'UserTableID':[]})

        #     # Add records to group
        #     group_records[-1]['UserTableID'].append(sorted_records[i]['id'])

    def test_write(self):
        self.table.create({'Name': 'John'})

    def closeness_score(self, locations):
        # Mapping of locations to their angles in radians
        loc_to_angle = {
            'N': 0,
            'NE': math.pi / 4,
            'E': math.pi / 2,
            'SE': 3 * math.pi / 4,
            'S': math.pi,
            'SW': -3 * math.pi / 4,
            'W': -math.pi / 2,
            'NW': -math.pi / 4,
            'C': None  # 'C' has no unique angle
        }

        # Compute average x and y position for the group excluding 'C' users
        avg_x, avg_y = 0, 0
        non_c_count = 0
        for loc in locations:
            angle = loc_to_angle[loc]
            if angle is not None:  # Only add contributions of non-'C' users
                avg_x += math.cos(angle)
                avg_y += math.sin(angle)
                non_c_count += 1

        # Divide by the total number of users, not just non-'C' users
        avg_x /= len(locations)
        avg_y /= len(locations)

        # Measure the distance from the average position to the center
        distance_to_center = math.sqrt(avg_x**2 + avg_y**2)

        closeness = 1.0 - distance_to_center

        return closeness

    def get_group_records(self):
        group_records = self.group_table.all()
        return group_records

    def get_all_records(self):
        records = self.table.all()
        return records

    def update_group_records(self, updated_group_records):
        self.group_table.batch_update(updated_group_records)

    def update_all_records(self, updated_all_records):
        self.table.batch_update(updated_all_records)




if __name__ == "__main__":
    random.seed(2)
    value = ''
    column_names = ''
    rows = ''
    with open('../../db.txt', 'rb') as f:
        column_names, rows = pickle.load(f)

    load_dotenv()
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    airtable = CommonlyAirtable(AIRTABLE_API_KEY)
    airtable.delete_all_data()
    airtable.send_data_to_airtable(column_names, rows)
    airtable.advanced_record_match("Week1")
    #airtable.set_matched_users("Week1")
    while(1):
        pass
    # print(rows)
    airtable.delete_all_data()
    airtable.send_data_to_airtable(column_names, rows)
    #airtable.simple_record_match("Week1")
    # Examples
    #airtable.advanced_record_match("Week1")
    initial_temperature = 4000
    cooling_rate = 0.996
    num_iterations = 10000
    best_groups, best_overflow = airtable.simulated_annealing(initial_temperature, cooling_rate, num_iterations)

    for records in best_groups: 
        for record in records:
            print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])
        print("\n")

    print("Overflow")
    for record in best_overflow:
        print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])
    print("\n")
    #dump_to_csv(column_names, rows)
    #test_write()
    #fetch_all()
    #process_records()
    #simple_record_match()


