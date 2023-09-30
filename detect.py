import requests
import cv2
import pymysql
import threading

url = "http://192.168.1.102:24405/"  # 边缘计算节点的地址
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


count = 0
# 定义一个函数来捕捉视频帧并进行处理
def capture_and_process_frames(url,params):
    global count
    while True:
        count += 1
        ret, frame = video_capture.read()
        if not ret:
            break
        if count % 10 == 0:
            # 发送图像数据到图像检测接口
            detect_and_send_image(url,params,frame)

        cv2.imshow('Video', frame)

        # 按'q'键退出视频捕捉
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# 向边缘计算服务发送请求
def detect_and_send_image(url,frame,params):
    # 将图像数据转换为二进制格式
    binary_image = cv2.imencode('.jpg', frame)[1].tobytes()
    response = requests.post(url,params=params, data=binary_image)

    # 处理图像检测接口的响应，这里可以根据需要进行进一步的处理
    data = response.json()
    print("图像检测结果:", data)

    # 解析resp 获取result、score
    confidence = data["results"][0]["confidence"]
    score = data["results"][0]["score"]
    label = data["results"][0]["label"]
    save_data(confidence, score,label)


# 数据存储至数据库
def save_data(confidence, score,label):

    try:
        sql_insert = """insert into image_data(confidence, score,label) values(%s,%s,%s)"""
        cursor.execute(sql_insert,(confidence, score,label))

    except:
        print("数据库存储异常")

    finally:
        conn.commit()  # 提交请求，不然不会插入数据


if __name__ == '__main__':
    global frame
    # 读取视频文件或摄像头
    video_capture = cv2.VideoCapture(0)

    # 创建两个线程，一个用于捕捉和处理视频帧，另一个用于发送图像数据到检测接口
    video_thread = threading.Thread(target=capture_and_process_frames,args=(url,params))
    image_detection_thread = threading.Thread(target=detect_and_send_image, args=(url,frame,params))

    # 启动线程
    video_thread.start()
    image_detection_thread.start()

    # 等待两个线程结束
    video_thread.join()
    image_detection_thread.join()

    conn.close()