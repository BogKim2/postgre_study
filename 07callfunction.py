import psycopg2
from config import load_config


def create_function_from_file():
    """ Create PostgreSQL function from SQL file """
    sql_file = 'get_parts_by_vendor.sql'
    config = load_config()

    try:
        with open(sql_file, 'r') as file:
            sql = file.read()

        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
                print("Function created successfully")

    except FileNotFoundError:
        print(f"SQL file not found: {sql_file}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating function: {error}")


def get_parts(vendor_id):
    """ Get parts provided by a vendor specified by the vendor_id """
    parts = []
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Call the stored procedure
                cur.callproc('get_parts_by_vendor', (vendor_id,))

                # Fetch all results
                rows = cur.fetchall()
                for row in rows:
                    parts.append({
                        'part_id': row[0],
                        'part_name': row[1]
                    })

                if parts:
                    print(f"\nParts supplied by vendor {vendor_id}:")
                    print("-" * 40)
                    for part in parts:
                        print(f"Part ID: {part['part_id']}, Name: {part['part_name']}")
                else:
                    print(f"\nNo parts found for vendor {vendor_id}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error getting parts: {error}")

    return parts
# 사용 예시:
if __name__ == '__main__':
    # 먼저 함수 생성
    create_function_from_file()

    # 그 다음 함수 사용
    parts = get_parts(1)