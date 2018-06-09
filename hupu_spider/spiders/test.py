# -*- coding: utf-8 -*-

from hupu_spider import db_connection_pool as pool


def getByPostId(id):
    select_sql = "select id from hupu_post where hupu_post_id=%s" % id

    with pool.get_db_connect() as db:
        try:
            db.cursor.execute(select_sql)
            results = db.cursor.fetchone()
            return results
        except:
            print("Error: unable to fecth data")

    return None


if __name__ == "__main__":
    post_id = getByPostId(1)
    print(post_id)
