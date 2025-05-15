import sqlite3
import math

def analyze_robot_trajectory():
    conn = sqlite3.connect('robot.db')
    cursor = conn.cursor()
    
    try:
        # 1. Find regions where Astro and IamHuman are close
        print("\nClose Proximity Regions (x_min, x_max, y_min, y_max):")
        print("-" * 80)
        
        # First get all timestamps where they're close
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
        
        # Then find continuous time blocks
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
        
        # Now get spatial regions for each time block
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
        
        # 2. Calculate total time they were close
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
        print(f"\nTotal time Astro and IamHuman were close: {total_seconds} seconds")
        
        # 3. New task: Check robot speeds during target intervals (simplified without event type)
        print("\nRobot Speed Analysis During Target Intervals:")
        print("{:<10} {:<15}".format("Interval", "Slow Speed (<0.2cm/s)"))
        print("-" * 30)
        
        # Get all target intervals (using rowid as interval_id)
        cursor.execute('''
            SELECT rowid, start_time, end_time 
            FROM target_intervals
            ORDER BY rowid
        ''')
        
        intervals = cursor.fetchall()
        
        for interval_id, start, end in intervals:
            cursor.execute("SELECT DISTINCT robot_id FROM robots")
            robot_ids = [row[0] for row in cursor.fetchall()]
            
            slow_detected = False
            
            for robot_id in robot_ids:
                # Get positions at start and end of interval
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
                    # Calculate distance and speed
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    distance = math.sqrt(dx**2 + dy**2)
                    duration = end - start
                    speed = distance / duration if duration > 0 else 0
                    
                    if speed < 0.2:
                        slow_detected = True
                        break
            
            print("{:<10} {:<15}".format(interval_id, "Yes" if slow_detected else "No"))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up temporary table
        cursor.execute("DROP TABLE IF EXISTS close_times")
        conn.close()

if __name__ == "__main__":
    analyze_robot_trajectory()