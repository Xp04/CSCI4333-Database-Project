import sqlite3

def print_robot_info():
    #Connects to the existing database
    conn = sqlite3.connect('robot.db')
    cursor = conn.cursor()
    
    try:
        #First is the x-axis max's and min's
        print("\nRobot X-axis Max and Min:")
        print("{:<12} {:<15} {:<15}".format("Robot Name", "Max X-axis", "Min X-axis"))
        print("-" * 42)
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
            ORDER BY
                r.name
        ''')
        for row in cursor.fetchall():
            print("{:<12} {:<15} {:<15}".format(row[0], row[1], row[2]))
        
        #Second is the y-axis max's and min's
        print("\nRobot Y-axis Max and Min:")
        print("{:<12} {:<15} {:<15}".format("Robot Name", "Max Y-axis", "Min Y-axis"))
        print("-" * 42)
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
            ORDER BY
                r.name
        ''')
        for row in cursor.fetchall():
            print("{:<12} {:<15} {:<15}".format(row[0], row[1], row[2]))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print_robot_info()