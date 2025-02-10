import psycopg2
from config import load_config
def create_procedure_from_file():
    """ Create PostgreSQL procedure from SQL file """
    sql_file = 'add_new_part.sql'
    config = load_config()

    try:
        # Read SQL file
        with open(sql_file, 'r') as file:
            sql = file.read()

        # Create procedure
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
                print("Procedure created successfully")

    except FileNotFoundError:
        print(f"SQL file not found: {sql_file}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating procedure: {error}")


def add_part(part_name, vendor_name):
    """ Add a new part with its vendor """
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Call the stored procedure
                cur.execute('CALL add_new_part(%s, %s)',
                            (part_name, vendor_name))
                conn.commit()
                print(f"Successfully added part '{part_name}' with vendor '{vendor_name}'")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding part: {error}")


if __name__ == '__main__':
    # First create the procedure
    create_procedure_from_file()

    # Then test it
    add_part('OLED', 'LG')