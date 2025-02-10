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


def get_vendors():
    """ Retrieve data from the vendors table """
    sql = "SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_id"
    config = load_config()
    vendors = []

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()

                for row in rows:
                    vendors.append({
                        'vendor_id': row[0],
                        'vendor_name': row[1]
                    })

                if not vendors:
                    print("No vendors found")
                else:
                    print(f"Retrieved {len(vendors)} vendors")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error retrieving vendors: {error}")

    return vendors


def get_vendors_fetchall():
    """ Retrieve data from the vendors table by fetchall """
    sql = "SELECT * FROM vendors ORDER BY vendor_id"
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                print("The number of parts: ", cur.rowcount)
                rows = cur.fetchall()

                print("\nVendor list:")
                for row in rows:
                    print(row)

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error retrieving vendors: {error}")


def add_part(part_name, vendors_id):
    """ Insert a new part and assign vendors to it """
    # SQL for inserting a part
    part_sql = """
        INSERT INTO parts(part_name)
        VALUES(%s)
        RETURNING part_id;
    """

    # SQL for inserting vendor parts
    vendor_part_sql = """
        INSERT INTO vendor_parts(vendor_id, part_id)
        VALUES(%s, %s)
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            # Create a cursor
            cur = conn.cursor()

            # Insert the part and get the part id
            cur.execute(part_sql, (part_name,))
            part_id = cur.fetchone()[0]

            # Insert vendor parts
            for vendor_id in vendors_id:
                cur.execute(vendor_part_sql, (vendor_id, part_id))

            # Commit the transaction
            conn.commit()

            print(f"Successfully added part '{part_name}' with ID: {part_id}")
            print(f"Assigned to vendors: {vendors_id}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding part: {error}")

    finally:
        if conn is not None:
            conn.close()


def get_parts_and_vendors():
    """ Get all parts and their associated vendors """
    sql = """
    SELECT 
        p.part_id,
        p.part_name,
        array_agg(v.vendor_name) as vendors
    FROM 
        parts p
        LEFT JOIN vendor_parts vp ON p.part_id = vp.part_id
        LEFT JOIN vendors v ON vp.vendor_id = v.vendor_id
    GROUP BY 
        p.part_id, p.part_name
    ORDER BY 
        p.part_id;
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()

                print("\nParts and their Vendors:")
                print("-" * 70)
                print(f"{'Part ID':<8} {'Part Name':<20} {'Vendors':<40}")
                print("-" * 70)

                for row in rows:
                    part_id, part_name, vendors = row
                    vendors_str = ', '.join(vendors) if vendors[0] is not None else 'No vendors'
                    print(f"{part_id:<8} {part_name:<20} {vendors_str:<40}")

                print("-" * 70)

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error retrieving parts and vendors: {error}")


# 사용 예시:
if __name__ == '__main__':
    get_parts_and_vendors()

# 사용 예시:
# if __name__ == '__main__':
#     # Add a new part and assign it to vendors 1 and 2
#     parts_to_add = [
#         ('SIM Tray', (1, 2)),
#         ('Speaker', (3, 4)),
#         ('Vibrator', (5, 6)),
#         ('Antenna', (6, 7)),
#         ('Home Button', (1, 5)),
#         ('LTE Modem', (1, 5))
#     ]
#
#     for part_name, vendor_ids in parts_to_add:
#         add_part(part_name, vendor_ids)