
import os
import requests
import time
import pymysql



def take_phote():
    # 执行命令行命令
    os.system('fswebcam -S 10 -r 640x480 ./tmp.jpg')
    print("拍摄成功")

def get_photo(url):
    with open('./tmp.jpg', 'rb') as f:
        img_data = f.read()
        result = requests.post(
            url=url,  # 请确认IP地址是否正确
            params=params,
            data=img_data)
        return result.json()

if __name__ == '__main__':
    # 连接数据库
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,  # 端口号
        user="root",  # 数据库用户
        password="123456",  # 数据库密码
        database="image_data"  # 要连接的数据库名称
    )
    cursor = conn.cursor()

    url = "http://localhost:24405/"  # 边缘计算节点的地址
    params = {'threshold': 0.1}

    for i in range(10):
        print("准备拍照")
        time.sleep(5)
        take_phote()
        print("拍照完成")
        time.sleep(1)
        data = get_photo(url)

        confidence = data["results"][0]["confidence"]
        score = data["results"][0]["score"]
        label = data["results"][0]["label"]

        sql_insert = """insert into test(confidence,score,label) values(%s,%s,%s)"""
        cursor.execute(sql_insert, (confidence, score, label))
        conn.commit()  # 提交请求，不然不会插入数据

