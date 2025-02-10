import psycopg2
from graphviz import Digraph
from config import load_config


def visualize_db_structure():
    """Create a database structure visualization"""

    # Create a new directed graph
    dot = Digraph(comment='Database Structure')
    dot.attr(rankdir='LR')  # Left to Right direction

    try:
        # Connect to database
        config = load_config()
        conn = psycopg2.connect(**config)
        cur = conn.cursor()

        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()

        # For each table, get its columns
        for table in tables:
            table_name = table[0]

            # Get columns for this table
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table_name,))
            columns = cur.fetchall()

            # Create table node
            table_label = f"{table_name}\\n"
            for col in columns:
                pk_marker = "*" if "id" in col[0] else " "  # Simple PK detection
                table_label += f"{pk_marker}{col[0]} ({col[1]})\\n"

            dot.node(table_name, table_label)

        # Get foreign key relationships
        cur.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY'
        """)

        # Add edges for foreign key relationships
        for fk in cur.fetchall():
            dot.edge(
                fk[0],  # table name
                fk[2],  # foreign table name
                f"{fk[1]} -> {fk[3]}"  # label: column -> foreign column
            )

        # Save the visualization
        dot.render('database_structure', format='png', cleanup=True)
        print("Database structure visualization has been saved as 'database_structure.png'")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    visualize_db_structure()