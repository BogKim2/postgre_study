from configparser import ConfigParser
import psycopg2


def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        raise Exception(f'Section {section} not found in {filename}')

    # Dictionary comprehension으로 더 간단하게 작성
    return {param[0]: param[1] for param in parser.items(section)}


def connect(config):
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        conn = psycopg2.connect(**config)
        print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error connecting to database: {error}")
        if conn is not None:
            conn.close()
        raise


def create_tables():
    """Create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS parts (
            part_id SERIAL PRIMARY KEY,
            part_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS part_drawings (
            part_id INTEGER PRIMARY KEY,
            file_extension VARCHAR(5) NOT NULL,
            drawing_data BYTEA NOT NULL,
            FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS vendor_parts (
            vendor_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            PRIMARY KEY (vendor_id, part_id),
            FOREIGN KEY (vendor_id)
                REFERENCES vendors (vendor_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
    )

    conn = None
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        cur = conn.cursor()

        # execute the CREATE TABLE statements
        for command in commands:
            cur.execute(command)

        cur.close()
        conn.commit()

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error creating tables: {error}")
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()

def insert_vendor(vendor_name):
    """ Insert a new vendor into the vendors table """
    sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
    vendor_id = None
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.execute(sql, (vendor_name,))
                # get the generated id back
                rows = cur.fetchone()
                if rows:
                    vendor_id = rows[0]
                # commit the changes to the database
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return vendor_id
def insert_many_vendors(vendor_list):
    """ Insert multiple vendors into the vendors table  """

    sql = "INSERT INTO vendors(vendor_name) VALUES(%s) RETURNING *"
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.executemany(sql, vendor_list)

            # commit the changes to the database
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def print_vendors():
    """ Print all vendors from the vendors table """
    sql = "SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_id"
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()

                if not rows:
                    print("No vendors found in the database.")
                else:
                    print("\nVendors List:")
                    print("-" * 40)
                    print(f"{'ID':<5} {'Name':<35}")
                    print("-" * 40)
                    for row in rows:
                        print(f"{row[0]:<5} {row[1]:<35}")
                    print("-" * 40)
                    print(f"Total vendors: {len(rows)}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching vendors: {error}")


def update_vendor(vendor_id, vendor_name):
    """ Update vendor name based on the vendor id """
    sql = """
    UPDATE vendors 
    SET vendor_name = %s 
    WHERE vendor_id = %s
    RETURNING vendor_id, vendor_name;
    """
    config = load_config()
    updated_vendor = None

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Execute the UPDATE statement
                cur.execute(sql, (vendor_name, vendor_id))

                # Get the updated row
                result = cur.fetchone()
                print(result)

                if result:
                    updated_vendor = {
                        'vendor_id': result[0],
                        'vendor_name': result[1]
                    }
                    print(f"Vendor updated successfully: {updated_vendor}")
                else:
                    print(f"No vendor found with id: {vendor_id}")

                conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error updating vendor: {error}")

    return updated_vendor


# 사용 예시:
if __name__ == '__main__':
    # 벤더 ID 1의 이름을 업데이트
    update_vendor(1, "3M company")
    try:
        print_vendors()
    except Exception as error:
        print(f"Failed to print vendors: {error}")

# # You can add this to your main block to test:
# if __name__ == '__main__':
#     try:
#         print_vendors()
#     except Exception as error:
#         print(f"Failed to print vendors: {error}")
# if __name__ == '__main__':
#     try:
#         # insert_vendor("3M Co.")
#         insert_many_vendors([
#             ('AKM Semiconductor Inc.',),
#             ('Asahi Glass Co Ltd.',),
#             ('Daikin Industries Ltd.',),
#             ('Dynacast International Inc.',),
#             ('Foster Electric Co. Ltd.',),
#             ('Murata Manufacturing Co. Ltd.',)
#         ])
#         print("insert vendor sucessfully")
#     except Exception as error:
#         print(f"Failed to create tables: {error}")


# if __name__ == '__main__':
#     try:
#         create_tables()
#         print("Tables created successfully")
#     except Exception as error:
#         print(f"Failed to create tables: {error}")