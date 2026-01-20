
    conn = get_database()
    cursor = conn.cursor()
    products = cursor.execute("select * from product").fetchall()
    conn.commit()
