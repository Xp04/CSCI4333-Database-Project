import sqlite3

def print_robot_info():
    # Connect to the existing database
    conn = sqlite3.connect('robot.db')
    cursor = conn.cursor()
    
    try:
        # Verify the required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='robots'")
        if not cursor.fetchone():
            raise ValueError("robots table not found in the database")
            
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_readings'")
        if not cursor.fetchone():
            raise ValueError("sensor_readings table not found in the database")

        # X-axis extremes
        print("\nRobot X-axis Extremes:")
        print("{:<10} {:<15} {:<15}".format("Name", "Max X-axis", "Min X-axis"))
        print("-" * 40)
        cursor.execute('''
            SELECT 
                r.name,
                MAX(sr.x_axis) AS max_x_axis,
                MIN(sr.x_axis) AS min_x_axis
            FROM 
                robots r
            JOIN 
                sensor_readings sr ON r.robot_id = sr.robot_id
            GROUP BY 
                r.robot_id, r.name
        ''')
        for row in cursor.fetchall():
            print("{:<10} {:<15} {:<15}".format(row[0], str(row[1]), str(row[2])))
        
        # Y-axis extremes
        print("\nRobot Y-axis Extremes:")
        print("{:<10} {:<15} {:<15}".format("Name", "Max Y-axis", "Min Y-axis"))
        print("-" * 40)
        cursor.execute('''
            SELECT 
                r.name,
                MAX(sr.y_axis) AS max_y_axis,
                MIN(sr.y_axis) AS min_y_axis
            FROM 
                robots r
            JOIN 
                sensor_readings sr ON r.robot_id = sr.robot_id
            GROUP BY 
                r.robot_id, r.name
        ''')
        for row in cursor.fetchall():
            print("{:<10} {:<15} {:<15}".format(row[0], str(row[1]), str(row[2])))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print_robot_info()