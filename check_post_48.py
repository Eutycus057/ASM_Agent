import sqlite3
import json

def check_post(post_id):
    conn = sqlite3.connect('prototype_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    if row:
        print(f"Post {post_id} details:")
        for key in row.keys():
            val = row[key]
            if key in ['analysis', 'draft'] and val:
                try:
                    val = json.loads(val)
                    print(f"  {key}: {json.dumps(val, indent=2)}")
                except:
                    print(f"  {key}: {val}")
            else:
                print(f"  {key}: {val}")
    else:
        print(f"Post {post_id} not found.")
    conn.close()

if __name__ == "__main__":
    check_post(48)
