import sqlite3
import math

def analyze_robot_trajectory():
    conn = sqlite3.connect('robot.db')
    cursor = conn.cursor()
    
    try:
        #First is finding the regions where Astro and IamHuman are close
        print("\nClose Distance Regions (x_min, x_max, y_min, y_max):")
        print("-" * 80)
        
        #All timestamps where they're close are collected
        cursor.execute('''
            CREATE TEMP TABLE close_times AS
            SELECT DISTINCT a.timestamp
            FROM sensor_readings a
            JOIN robots ra ON a.robot_id = ra.robot_id AND ra.name = 'Astro'
            JOIN sensor_readings b ON a.timestamp = b.timestamp
            JOIN robots rb ON b.robot_id = rb.robot_id AND rb.name = 'IamHuman'
            WHERE ABS(a.x_axis - b.x_axis) < 1 
              AND ABS(a.y_axis - b.y_axis) < 1
            ORDER BY a.timestamp
        ''')
        
        #Find continuous time stamps
        cursor.execute('''
            SELECT 
                MIN(timestamp) AS start_time,
                MAX(timestamp) AS end_time
            FROM (
                SELECT timestamp,
                       timestamp - ROW_NUMBER() OVER (ORDER BY timestamp) AS grp
                FROM close_times
            )
            GROUP BY grp
        ''')
        
        time_blocks = cursor.fetchall()
        
        #Getting the spatial regions for each time stamp
        for start, end in time_blocks:
            cursor.execute('''
                SELECT 
                    MIN(a.x_axis) AS x_min,
                    MAX(a.x_axis) AS x_max,
                    MIN(a.y_axis) AS y_min,
                    MAX(a.y_axis) AS y_max
                FROM sensor_readings a
                JOIN robots ra ON a.robot_id = ra.robot_id AND ra.name = 'Astro'
                WHERE a.timestamp BETWEEN ? AND ?
            ''', (start, end))
            
            region = cursor.fetchone()
            print(f"Time: {start}-{end}s | x: [{region[0]}, {region[1]}] y: [{region[2]}, {region[3]}]")
        
        #Second is to then calculate the total time they were close
        cursor.execute('''
            SELECT COUNT(DISTINCT a.timestamp)
            FROM sensor_readings a
            JOIN robots ra ON a.robot_id = ra.robot_id AND ra.name = 'Astro'
            JOIN sensor_readings b ON a.timestamp = b.timestamp
            JOIN robots rb ON b.robot_id = rb.robot_id AND rb.name = 'IamHuman'
            WHERE ABS(a.x_axis - b.x_axis) < 1 
              AND ABS(a.y_axis - b.y_axis) < 1
        ''')
        
        total_seconds = cursor.fetchone()[0]
        print(f"\nTotal time Astro and IamHuman were close is: {total_seconds} seconds")
        
        #Third(bonus) is to check for robot speeds during the target intervals
        print("\nRobot Speed During Target Intervals:")
        print("{:<10} {:<15} {:<15}".format("Interval", "Start-End", "Slow Speed (<0.2cm/s)"))
        print("-" * 45)
        
        #All target intervals
        cursor.execute('''
            SELECT rowinterval_id, start_time, end_time 
            FROM target_intervals
            ORDER BY rowinterval_id
        ''')
        
        intervals = cursor.fetchall()
        
        for rowinterval_id, start, end in intervals:
            cursor.execute("SELECT DISTINCT robot_id FROM robots")
            robot_ids = [row[0] for row in cursor.fetchall()]
            
            slow_detected = False
            
            for robot_id in robot_ids:
                #Positions at start and end of interval are gotten
                cursor.execute('''
                    SELECT x_axis, y_axis FROM sensor_readings 
                    WHERE robot_id = ? AND timestamp = ?
                ''', (robot_id, start))
                start_pos = cursor.fetchone()
                
                cursor.execute('''
                    SELECT x_axis, y_axis FROM sensor_readings 
                    WHERE robot_id = ? AND timestamp = ?
                ''', (robot_id, end))
                end_pos = cursor.fetchone()
                
                if start_pos and end_pos:
                    #Handles calculating the distance and speed
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    distance = math.sqrt(dx**2 + dy**2)
                    duration = end - start
                    speed = distance / duration if duration > 0 else 0
                    
                    if speed < 0.2:
                        slow_detected = True
                        break
            
            print("{:<10} {:<5}-{:<5} {:<15}".format(
                rowinterval_id, 
                start, 
                end, 
                "Yes" if slow_detected else "No"))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        #Cleans up temporary table(issue I was having in printing duplicate tables)
        cursor.execute("DROP TABLE IF EXISTS close_times")
        conn.close()

if __name__ == "__main__":
    analyze_robot_trajectory()