import sqlite3
import pandas as pd
import csv

def create_robot_db():
    # Create or connect to the database
    conn = sqlite3.connect('robot.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS robots (
        robot_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_readings (
        reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id INTEGER NOT NULL,
        timestamp INTEGER NOT NULL,
        x_axis REAL NOT NULL,
        y_axis REAL NOT NULL,
        FOREIGN KEY (robot_id) REFERENCES robots (robot_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS target_intervals (
        interval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time INTEGER NOT NULL,
        end_time INTEGER NOT NULL,
        event_type TEXT NOT NULL
    )
    ''')
    
    # Import data from CSV files
    try:
        # Import robot data (assuming columns are robot_id and name in order)
        with open('robot.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute("INSERT INTO robots (robot_id, name) VALUES (?, ?)", 
                              (int(row[0]), row[1]))
        
        # Import sensor readings from t1.csv to t5.csv
        for robot_id in range(1, 6):
            file_name = f't{robot_id}.csv'
            with open(file_name, 'r') as f:
                reader = csv.reader(f)
                for timestamp, row in enumerate(reader, start=1):
                    x_axis, y_axis = map(float, row)
                    cursor.execute('''
                        INSERT INTO sensor_readings 
                        (robot_id, timestamp, x_axis, y_axis) 
                        VALUES (?, ?, ?, ?)
                    ''', (robot_id, timestamp, x_axis, y_axis))
        
        # Import target intervals (assuming columns are start_time, end_time, event_type in order)
        with open('interval.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute('''
                    INSERT INTO target_intervals 
                    (start_time, end_time, event_type) 
                    VALUES (?, ?, ?)
                ''', (int(row[0]), int(row[1]), row[2]))
        
        print("Database created and data imported successfully!")
    
    except Exception as e:
        print(f"Error importing data: {e}")
        conn.rollback()
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    create_robot_db()

