import json
import pymysql


def insert_organizer(filename):
    file = open(filename)
    i = 0
    j = 0
    data_list = []
    db = pymysql.connect(host="127.0.0.1", user="root", passwd="123456", port=3306, db="test", charset='utf8')
    cursor = db.cursor()
    sql = "insert into organizer(oid, name, description, event_count, member) values (%s, %s, %s, %s, %s)"
    for line in file:
        row = line.strip().strip(",")
        obj = json.loads(row)
        data_list.append((obj['id'], obj['name'], obj['description'], obj['event_count'], obj['member']))
        if i > 5000:
            cursor.executemany(sql, data_list)
            db.commit()
            i = 0
            data_list = []
        i = i + 1
        j = j + 1
    if i > 0:
        cursor.executemany(sql, data_list)
        db.commit()
    db.close()
    file.close()


def insert_event(filename):
    file = open(filename)
    i = 0
    j = 0
    data_list = []
    db = pymysql.connect(host="127.0.0.1", user="root", passwd="123456", port=3306, db="test", charset='utf8')
    cursor = db.cursor()
    sql = "insert into event(oid, name, description, event_count, member) values (%s, %s, %s, %s, %s)"
    for line in file:
        row = line.strip().strip(",")
        obj = json.loads(row)
        data_list.append((obj['id'], obj['name'], obj['description'], obj['event_count'], obj['member']))
        if i > 5000:
            cursor.executemany(sql, data_list)
            db.commit()
            i = 0
            data_list = []
        i = i + 1
        j = j + 1
    if i > 0:
        cursor.executemany(sql, data_list)
        db.commit()
    db.close()
    file.close()

if __name__ == "__main__":
    insert_organizer("/Users/mac/Desktop/file/org-log.txt")
