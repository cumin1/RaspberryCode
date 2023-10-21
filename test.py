import cv2
import pymysql
import threading
import requests

url = "http://127.0.0.1:8702"
params = {'threshold': 0.1}

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="123456",
    database=""
)
cursor = conn.cursor()


def send_data(frame,url):
    cv2.imwrite("tmp.jpg",frame)
    with open("tmp.jpg","wb") as f:
        img = f.read()
        response = requests.post(url=url,params=params,data=img).json()
        confidence = response["confidence"]
        label = response["label"]
        print(confidence,label)
        save_data(confidence,label)

def save_data(confidence,label):
    sql = """"insert into table(confidence,label) values(%s,%s)"""
    cursor.execute(sql,(confidence,label))
    conn.commit()


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    while True:
        ret,frame = cap.read()
        if not ret:
            print("没有读取到图像")
            break


        if cv2.waitKey(1) == ord("w"):
            threading.Thread(save_data,args=(frame,url)).start()

        if cv2.waitKey(1) == ord("q"):
            break






