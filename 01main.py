import psycopg2
import time

try:
    conn = psycopg2.connect(
        host='localhost',
        database='mydb',
        user='postgres',
        password='99013835',
        port=5432        # 문자열이 아닌 정수로 변경
    )
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM myvolt2')
    conn.commit()
    result = cur.fetchone()
    print(result[0])
    measTime = int(time.time())
    volt = 3.7
    cur.execute(f'UPDATE myvolt2 SET "time"={measTime}, volt={volt} WHERE id=4 ')
    conn.commit()

    cur.execute('SELECT id, time, volt FROM myvolt2') # SQL에 0번은 meas_time, 1번은 volt
    conn.commit()
    result = cur.fetchall() # 튜플을 원소로 가진 리스트
    print(result)

except psycopg2.Error as e:
    print(f"데이터베이스 오류: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()



# # DB를 다 쓰고 나면 cursor와 connection 닫기
# cur.close()
# conn.close()
#
#
# # 각 column에 data 삽입
# measTime = int(time.time())
# volt = 3.7
# cur.execute(f'INSERT INTO volt_table(meas_time, volt) VALUES({measTime}, {volt})')
# conn.commit()
#
# # 현재 시간 읽기
# import time
# nTime = int(time.time()) # 현재 에포크 타임(epoch time: 1970년 기점으로 측정한 시간)
# print(nTime)
#
#
# # 각 column의 data를 읽어오기
# cur.execute('SELECT meas_time, volt FROM volt_table') # SQL에 0번은 meas_time, 1번은 volt
# conn.commit()
#
#
# # DB 실행 결과 전부(all)를 획득(fetch)
# result = cur.fetchall() # 튜플을 원소로 가진 리스트
# print(result)
#
#
# measTime = result[0][0] # meas_time: 0번 row(튜플)의 0번 값(측정 시간)
# print(measTime)
#
#
# volt = result[0][1] # meas_time: 0번 row(튜플)의 1번 값(전압)
# print(volt)
#
#
# # table의 모든 원소 자르기(삭제)
# cur.execute('TRUNCATE volt_table')
# conn.commit()
