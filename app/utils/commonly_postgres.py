import psycopg2
import pickle
import csv

class CommonlyPostgres():
    def __init__(self, pg_host, pg_password, pg_database):
        self.pg_host = pg_host
        self.pg_password = pg_password
        self.pg_database = pg_database

    def fetch_data_from_postgres(self):

        connection = psycopg2.connect(
            host=self.pg_host,
            port="5432",
            user="read_only_user",
            password=self.pg_password,
            database=self.pg_database
        )

        cursor = connection.cursor()
        cursor.execute("SELECT \
            u.*, \
            ARRAY_AGG(TO_CHAR(ua.time, 'YYYY-MM-DD HH:MI:SS')) AS time_avail \
            FROM users u \
            LEFT JOIN user_availabilities ua \
            ON u.id = ua.user_id \
            WHERE ua.time IS NOT NULL \
            GROUP BY \
            u.id \
            ORDER BY \
            u.created_at \
            DESC \
            LIMIT \
            5")  # Replace 'your_table_name' with the name of your table
        rows = cursor.fetchall()

        # Fetch the column names (optional, but useful if you want to match with Airtable fields)
        column_names = [desc[0] for desc in cursor.description]

        connection.close()
        print(rows)
        return column_names, rows

    def fetch_venues_from_postgres(self):
        connection = psycopg2.connect(
            host=self.pg_host,
            port="5432",
            user="read_only_user",
            password=self.pg_password,
            database=self.pg_database
        )

        cursor = connection.cursor()
        cursor.execute("SELECT *\
    FROM venues \
    ORDER BY name")
        
        rows = cursor.fetchall()

        # Fetch the column names (optional, but useful if you want to match with Airtable fields)
        column_names = [desc[0] for desc in cursor.description]

        connection.close()
        print(rows)
        return column_names, rows

    def dump_to_csv(column_names, rows, filename='venues.csv'):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write the header
            writer.writerow(column_names)
            
            # Write the rows
            for row in rows:
                writer.writerow(row)

if __name__ == '__main__':
    #value = fetch_data_from_postgres()
    #with open('db_read.txt', 'wb') as f:
    #    pickle.dump(value, f)

    value = fetch_venues_from_postgres()
    print(value)
    print(type(value))
    with open('db_venues.txt', 'wb') as f:
        pickle.dump(value, f)
    
    dump_to_csv(value[0], value[1])