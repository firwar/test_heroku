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
#from sklearn.metrics import pairwise_distances
#from scipy.spatial.distance import cosine
# import spacy
from pyairtable import Table, Api
from dotenv import load_dotenv
 
class CommonlyAirtable():
    
    def __init__(self, api_key):

        self.AIRTABLE_BASE_ID = "appPrjUSEv6JdAeVJ"
        self.AIRTABLE_TABLE_NAME = "TestUsers"
        self.AIRTABLE_GROUP_TABLE_NAME = "TestGroups"

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

    def send_data_to_airtable(self, column_names, rows):
        # Function to convert individual row to Airtable record format
        def row_to_record(row):
            return {
                column_names[i]: (value.isoformat() if isinstance(value, (dt.date, dt.datetime)) else value)
                for i, value in enumerate(row)
            }


        start_date_str = "2022-11-14 00:00:00"
        end_date_str = "2022-11-20 23:59:59"

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")


        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
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
            records[i]['Status'] = "unmatched"
            records[i]['Week1'] = "unmatched"
            records[i]['Week2'] = "unmatched"
            records[i]['Week3'] = "unmatched"
            records[i]['Week4'] = "unmatched"
            records[i]['email_reg'] = True
            records[i]['email_match'] = False
            records[i]['Availability'] = []
            #records[i]['Availability'] = week_dates_avail[:]
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


    def simulated_annealing(self, initial_temperature, cooling_rate, num_iterations):
        #current_solution = generate_initial_solution(people)
        current_solution = self.advanced_record_match("Week1")
        current_energy = self.get_energy(current_solution)
        print("current energy: " + str(current_energy)) 
        best_solution = current_solution
        best_energy = current_energy

        T = initial_temperature
        
        for i in range(num_iterations):
            neighbor = self.generate_neighbor(current_solution)
            neighbor_energy = self.get_energy(neighbor)
            if (neighbor_energy >= 100000):
                continue
            print(str(i) + " neighbor_energy: " + str(current_energy))

            #potentially
            if neighbor_energy < current_energy:
                current_solution, current_energy = neighbor, neighbor_energy
            else:
                delta = neighbor_energy - current_energy
                probability = math.exp(-delta / T)
                
                if random.random() < probability:
                    current_solution, current_energy = neighbor, neighbor_energy
            
            if current_energy < best_energy:
                best_solution, best_energy = current_solution, current_energy

            T *= cooling_rate

        return best_solution


    # groups
    # [ [records1, record2, record3, record4 ]  , [  ]] 
    # [ records1. availabilities]
    def get_energy(self, groups):
        
        calculated_energy = 1000000
        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for i in range(len(groups)):
            outer_availability_found = False
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
                calculated_energy = 1000000
                return calculated_energy

        # have a calculation at the end for how well each group matches
        variance_total = 0
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
            variance_total += variance

        calculated_energy = variance_total 


        closeness_energy = 0
        for i in range(len(groups)):
            friendly_location_arr = []
            for j in range(len(groups[i])):
                friendly_location_arr.append(groups[i][j]['fields']['friendly_location'])
            closeness = self.closeness_score(friendly_location_arr) * 2000
            closeness_energy += closeness
            
        calculated_energy += closeness_energy
        return calculated_energy 
    # neighbor algorith
    # swap two people 
    # move one to different group


    def generate_neighbor(self, input_group):
        groups = copy.deepcopy(input_group)
        # Create a new solution by swapping two random people between groups,
        # moving a person from one group to another, or other random changes.
        #rand_value = random.randint(0,1)
        rand_value = 0
        # swap two
        if rand_value == 0:
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

        return groups

    def advanced_record_match(self, week_col_string):
        all_records = []

        all_records = self.table.all()

        friendly_location_circle = ['NW','N','NE','E','SE','S','SW','W']
        friendly_location = {}
    # id
    # availability
    # age
    # location    
        # Sort by age
        availability_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        availability_count = [0, 0, 0, 0, 0]
        all_records = list(filter(lambda record: record['fields']['friendly_location'] != 'Out of Range', all_records))
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
        group_records = []
        for day in availability_sorted:
            i = 0
            for record in all_records:
                if record['fields']['processed'] == False:
                    if day in record['fields']['Availability']:
                        if i % 5 == 0:
                            group_records.append([])
                        i += 1
                        group_records[-1].append(record)
                        record['fields']['processed'] = True
                        record['fields']['day'] = day

        print(len(group_records))
        for records in group_records: 
            for record in records:
                print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])

            print("")

        #group_records[-1][-1]['fields']['Availability'] = ['Saturday']
        #energy = self.get_energy(group_records)
        #print(energy)
        #self.generate_neighbor(group_records)
        return group_records

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

if __name__ == "__main__":
    random.seed(2)
    value = ''
    column_names = ''
    rows = ''
    with open('../../db.txt', 'rb') as f:
        column_names, rows = pickle.load(f)

    load_dotenv()
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    print(AIRTABLE_API_KEY)
    airtable = CommonlyAirtable(AIRTABLE_API_KEY)
    # print(rows)
    #airtable.delete_all_data()
    #airtable.send_data_to_airtable(column_names, rows)
    #airtable.simple_record_match("Week1")
    # Examples
    #airtable.advanced_record_match("Week1")
    initial_temperature = 3000
    cooling_rate = 0.99
    num_iterations = 10000
    best_groups = airtable.simulated_annealing(initial_temperature, cooling_rate, num_iterations)

    for records in best_groups: 
        for record in records:
            print(str(record['fields']['friendly_location']) + " " + str(record['fields']['age']) + " " + record['fields']['day'])
        print("\n")


    #dump_to_csv(column_names, rows)
    #test_write()
    #fetch_all()
    #process_records()
    #simple_record_match()


