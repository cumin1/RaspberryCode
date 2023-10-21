import time

import requests
import cv2
import pymysql
import threading

url = "http://127.0.0.1:24405/"  # 边缘计算节点的地址
params = {'threshold': 0.1}

# 连接数据库
conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="123456",
    database="image_data"
)
cursor = conn.cursor()


# 向边缘计算服务发送请求
def detect_and_send_image(url, params, frame):


    cv2.imwrite("tmp.jpg", frame)
    with open('./tmp.jpg', 'rb') as f:
        img_data = f.read()
        print(img_data)
        result = requests.post(
            url=url,  # 请确认IP地址是否正确
            params=params,
            data=img_data)

        # 处理图像检测接口的响应，这里可以根据需要进行进一步的处理
        data = result.json()
        print("图像检测结果:", data)

        # 解析resp 获取result、score
        confidence = data["results"][0]["confidence"]
        score = data["results"][0]["score"]
        label = data["results"][0]["label"]

        try:
            sql_insert = """insert into test(confidence, score,label) values(%f,%f,%s)"""
            cursor.execute(sql_insert, (confidence, score, label))
            conn.commit()  # 提交请求，不然不会插入数据
        except:
            print("数据库存储异常")


# 数据存储至数据库
# def save_data(confidence, score, label):


if __name__ == '__main__':
    # 读取视频文件或摄像头
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        if not ret:
            break

        # 发送图像数据到图像检测接

        if cv2.waitKey(1) & 0xFF == ord('w'): # 按住w拍照
            threading.Thread(target=detect_and_send_image, args=(url, params, frame)).start()
            # t = time.time()  # 更新结果时间

        cv2.imshow('Video', frame)

        # 按'q'键退出视频捕捉
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
