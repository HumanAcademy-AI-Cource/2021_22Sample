#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 必要なライブラリをインポート
import cv2
import subprocess
import roslib.packages
import boto3
import wave
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def card_reader(image_path):
    '''
    AWSのRekognitionを使用してカードの読み取りをする関数
    '''
    text = []
    # 表示用に再度画像を読み込む
    image = cv2.imread(image_path)
    # Rekognitionを利用するための準備
    rekognition = boto3.client(service_name="rekognition")
    # 引数（image_path）で指定された画像を読み込む
    with open(image_path, 'rb') as file:
        try:
            # rekognitionのdetect_textを利用して画像内の文字を認識
            detext_text_data = rekognition.detect_text(Image={'Bytes': file.read()})
            # 画像内に文字があった場合には処理を続行
            if len(detext_text_data["TextDetections"]) != 0:
                # 認識結果から認識した文字の情報だけ取り出す
                for d in detext_text_data["TextDetections"]:
                    if d["Type"] == "LINE":
                        x = int(d["Geometry"]["BoundingBox"]["Left"] * image.shape[1])
                        y = int(d["Geometry"]["BoundingBox"]["Top"] * image.shape[0])
                        w = int(d["Geometry"]["BoundingBox"]["Width"] * image.shape[1])
                        h = int(d["Geometry"]["BoundingBox"]["Height"] * image.shape[0])
                        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 241, 255), 3)
                        image = cv2.putText(image, d["DetectedText"], (x, y + h + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 241, 255), thickness=5)
                        text.append(d["DetectedText"])
                        
        except Exception as e:
            print("AWSが混み合っていますので、しばらくお待ちください。")
            time.sleep(int(random.uniform(0, 5)))
    # 文字データを返す
    return text, image


if __name__ == '__main__':
    detect_text, image = card_reader("./images/card.png")
    print("=======================================================================")
    print("○ 認識したカードの情報")
    for d in detect_text:
        print(d)
    print("=======================================================================")
    image = cv2.resize(image, (image.shape[1] / 2, image.shape[0] / 2))
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()