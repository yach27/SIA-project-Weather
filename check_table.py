"""Check if user_locations table exists in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_chatbot.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check if table exists
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'user_locations';
    """)
    result = cursor.fetchone()

    if result:
        print("Table 'user_locations' exists!")

        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'user_locations';
        """)
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")

        # Check if there's any data
        cursor.execute("SELECT COUNT(*) FROM user_locations;")
        count = cursor.fetchone()[0]
        print(f"\nTotal records: {count}")

    else:
        print("Table 'user_locations' does NOT exist!")
        print("\nAttempting to create table manually...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_locations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
                latitude NUMERIC(9, 6) NOT NULL,
                longitude NUMERIC(9, 6) NOT NULL,
                location_name VARCHAR(200),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        print("Table created successfully!")
