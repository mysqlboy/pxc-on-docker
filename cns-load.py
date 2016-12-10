#!/usr/local/python

import sys
import MySQLdb
import yaml
import json

reload(sys)
sys.setdefaultencoding('Cp1252')


from datetime import datetime
from elasticsearch import Elasticsearch, exceptions

def myconn():
    dbhost = '127.0.0.1'
    dbport =  3306
    dbuser = 'root'
    dbpass = 'root'
    schema = 'rdba'

    try:
        conn = MySQLdb.connect(host=dbhost,
                                port=dbport,
                                user=dbuser,
                                passwd=dbpass,
                                db=schema)
        return conn
    except MySQLdb.Error, e:
        print "Database Error: %s" % (e)

def format_date(data):
    """
    function to make a string to a date
    """
    print type(data)
    data = data.replace(' ','T')
    print data

    return data

def get_notifications():
    db = myconn()
    cur = db.cursor()
    query = """select
                    n.id,
                    ns.description,
                    n.summary,
                    u.username,
                    n.project_id as 'inc_assoc',
                    ps.description as 'inc_status',
                    c.name as 'client',
                    n.time as 'recieved_at',
                    n.ack_at,
                    timediff(ack_at,time) as 'TTA',
                    s.description as service
                    from notifications n
                    join services s on
                      s.id = n.service_id
                    join notification_status ns on
                      n.status_id = ns.id
                    join projects p on
                      n.project_id = p.id
                    join project_status ps on
                      ps.id = p.status_id
                    join users u on
                      n.ack_by = u.id
                    join clients c on
                      c.id = n.client_id
                    where n.id > %s
                    and n.status_id in (2,3,5)
                    and n.ready_for_pager is not null;
                    """
    sql = query % ('1542811')
    print "exec mysql query"
    cur.execute(sql)
    res = cur.fetchall()
    return res

    # def get_notes():
    #     db = myconn()
    #     cur = db.cursor()
    #     query = """select
    #                 nn.id,
    #                 nn.entry_datetime,
    #                 nn.component,
    #                 nn.message,
    #                 nn.project_id,
    #                 nn.notification_id,
    #                 c.name as 'client',
    #                 u.username
    #                 from internal_notes nn
    #                 join users u on
    #                   nn.user_id = u.id
    #                 join clients c on
    #                   c.id = nn.client_id
    #                 where nn.id > %s;
    #                 """
    #     sql = query % ('0')
    #     cur.execute(sql)
    #     res = cur.fetchall()
    #     return res

def index_notification(notification, es_connection):
    # print type(notification[8])
    # print notification[8]
    try:
        print "in function"
        es_connection.index(index="cns", doc_type="notification_new", id=notification[0], body={"severity":notification[1],
                                                                                "summary": notification[2],
                                                                                "username": notification[3],
                                                                                "incident": notification[4],
                                                                                "incident_status": notification[5],
                                                                                "client": notification[6],
                                                                                "received_at": notification[7],
                                                                                "ack_at": notification[8],
                                                                                "service": notification[10],
                                                                                })
    except Exception as e:
        print "%s" %(e)
        pass

# def index_notes(note, es_connection):
#     # print type(notification[8])
#     # print notification[8]
#     try:
#         es_connection.index(index="cns", doc_type="notes", id=note[0], body={"entry_datetime":note[1],
#                                                                                 "component": note[2],
#                                                                                 "message": unicode(note[3]),
#                                                                                 "project_id": note[4],
#                                                                                 "notification_id": note[5],
#                                                                                 "client": note[6],
#                                                                                 "username": note[7],
#                                                                                 })
#     except exceptions.RequestError, e:
#         print "Error: %s\n%s\n%s" % (e,note[0],note[3][0:100])

def main():

    es = Elasticsearch([{'host': 'http://127.0.0.1', 'port': 9200, 'timeout': 60}])
    notifications = get_notifications()
    print len(notifications)
    # notes = get_notes()
    #
    #
    # for note in notes:
    #     index_notes(note, es)
        # print unicode(note[3])
    print "exec es import"
    for i in notifications:
        print "in loop"
        res = index_notification(i, es)
        print i


if __name__ == '__main__':
    main()
