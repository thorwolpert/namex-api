from __future__ import print_function
from datetime import datetime
from config import Config

import cx_Oracle
import psycopg2
import psycopg2.extras

# connect to both databases
ora_con = cx_Oracle.connect(Config.ORA_USER,
                            Config.ORA_PASSWORD,
                            "{0}:{1}/{2}".format(Config.ORA_HOST, Config.ORA_PORT, Config.ORA_NAME))

pg_conn = psycopg2.connect("host='{0}' dbname='{1}' user='{2}' password='{3}' port='{4}'".
                           format(Config.PG_HOST, Config.PG_NAME, Config.PG_USER, Config.PG_PASSWORD, Config.PG_PORT))

# make sure PG is doing the roght level of transaction management
pg_conn.set_session(isolation_level='REPEATABLE READ', readonly=False, deferrable=False, autocommit=False)

start_time = datetime.utcnow()

pg_cur = pg_conn.cursor()

pg_cur.execute("select nextval('nro_job_seq')")
job_id = pg_cur.fetchone()[0]
state = 'running'

pg_cur.execute("""insert into nro_names_sync_job (id, status_cd, start_time, end_time) values (%s, %s, %s, %s);""",
               (job_id, state, start_time, 'epoch'))
pg_conn.commit()

try:

    ora_con.begin()
    ora_cursor = ora_con.cursor()

    pg_cur_track = pg_conn.cursor()

    pg_cursor = pg_conn.cursor('serverside_cursor_name', cursor_factory=psycopg2.extras.DictCursor)
    pg_cursor.execute("SELECT *, (SELECT username FROM users WHERE id=r.user_id) as username " +
                      ",(last_update::date + integer '60') as expiry_date "
                      "FROM requests r " +
                      "WHERE state in ('APPROVED', 'REJECTED', 'CANCELLED')" +
                      "  AND last_update >= 'epoch' " +
                      "LIMIT " + Config.MAX_ROW_LIMIT
                      )

    row_count = 0
    for pg_row in pg_cursor:
        row_count += 1

        try:
            ora_cursor.callproc("NRO_DATA_PUMP_PKG.name_examination",
                                    [pg_row['nr_num'],        #p_nr_number
                                     pg_row['state'],         #p_status
                                     pg_row['expiry_date'],   #p_expiry_date
                                     pg_row['consent_flag'],  #p_consent_flag
                                     pg_row['username'],      #p_examiner_id
                                     'NE',                    #p_choice1
                                     'NA',                    #p_choice2
                                     'NA',                    #p_choice3
                                     pg_row['admin_comment']] #p_exam_comment
                                )

            pg_cur_track.execute(
                """insert into nro_names_sync_job_detail (job_id, nr_num, time) values (%s, %s, %s);""",
                (job_id, pg_row['nr_num'], datetime.utcnow()))

        except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            print("NR#:", pg_row['nr_num'], "Oracle-Error-Code:", error.code)
            # print("Oracle-Error-Message:", error.message)
        except Exception as err:
            print("NR#:", pg_row['nr_num'], "Error:", err)

    # update the tracking status
    end_time = datetime.utcnow()
    state = 'success'
    pg_cur.execute("""update nro_names_sync_job set status_cd =%s, end_time=%s where id=%s;""",
                   (state, end_time, job_id))

    # commit and save the changes
    ora_con.commit()
    pg_conn.commit()

except Exception as err:
    # something went wrong, roll it all back
    #TODO: Notify ops of the error in sync
    print ('Exception:', err)
    ora_con.rollback()
    pg_conn.rollback()

finally:
    ora_con.close()
    pg_conn.close()

print("job - requests processed: {0} completed in:{1}".format(row_count, end_time-start_time))