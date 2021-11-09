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

def aws_detect_text(image_path):
    '''
    AWSのRekognitionを使用して画像内の文字を認識する関数
    '''
    # 表示用に再度画像を読み込む
    image = cv2.imread(image_path)
    # Rekognitionを利用するための準備
    rekognition = boto3.client(service_name="rekognition")
    # 引数（image_path）で指定された画像を読み込む
    with open(image_path, 'rb') as file:
        text = ""
        try:
            # rekognitionのdetect_textを利用して画像内の文字を認識
            detext_text_data = rekognition.detect_text(Image={'Bytes': file.read()})
            # 画像内に文字があった場合には処理を続行
            if len(detext_text_data["TextDetections"]) != 0:
                # 認識結果から認識した文字の情報だけ取り出す
                for d in detext_text_data["TextDetections"]:
                    if d["Type"] == "LINE":
                        text += d["DetectedText"]
                        x = int(d["Geometry"]["BoundingBox"]["Left"] * image.shape[1])
                        y = int(d["Geometry"]["BoundingBox"]["Top"] * image.shape[0])
                        w = int(d["Geometry"]["BoundingBox"]["Width"] * image.shape[1])
                        h = int(d["Geometry"]["BoundingBox"]["Height"] * image.shape[0])
                        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 241, 255), 3)
        except Exception as e:
            print("AWSが混み合っていますので、しばらくお待ちください。")
            time.sleep(int(random.uniform(0, 5)))
    # 文字データを返す
    return text, image


def aws_synthesize_speech(text, filepath):
    '''
    AWSのPollyを使用して文章を音声合成する関数
    '''
    polly = boto3.client(service_name="polly")
    speech_data = polly.synthesize_speech(
        Text=text,
        OutputFormat='pcm',
        VoiceId='Salli'
    )['AudioStream']
    wave_data = wave.open(filepath, 'wb')
    wave_data.setnchannels(1)
    wave_data.setsampwidth(2)
    wave_data.setframerate(16000)
    wave_data.writeframes(speech_data.read())
    wave_data.close()


if __name__ == '__main__':
    detect_text, image = aws_detect_text("./images/eigo.png")
    print("=======================================================================")
    print("○ 認識した文章: {}".format(detect_text))
    print("=======================================================================")
    print("[s]キーを押すと読み上げを開始します。")
    print("=======================================================================")
    cv2.imshow("image", image)
    cv2.waitKey(0)
    filename = "./speech.wav"
    aws_synthesize_speech(detect_text, filename)
    subprocess.check_call('aplay -D plughw:0 {}'.format(filename), shell=True)
    cv2.destroyAllWindows()