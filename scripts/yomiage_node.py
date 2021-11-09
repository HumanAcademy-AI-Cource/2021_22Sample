#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 必要なライブラリをインポート
import rospy
import cv2
import subprocess
import roslib.packages
import boto3
import wave
import csv
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import yomiage


class Yomiage(object):
    def __init__(self):
        rospy.Subscriber("/image_raw", Image, self.imageCB)
        self.image = None
        self.enable_process = 0
        self.pkg_path = roslib.packages.get_pkg_dir("aws_detect_text")


    def process(self):
        target_file = self.pkg_path + "/scripts/images/camera.jpg"
        cv2.imwrite(target_file, self.image)
        
        # 画像から文字を認識
        detect_text, image = yomiage.aws_detect_text(target_file)
        # 認識した文字を表示
        print("○ 認識した文章: {}".format(detect_text))
        print("=======================================================================")
        # 音声データを保存するパスを準備
        filepath = self.pkg_path + "/scripts/speech.wav"
        # 音声合成開始
        yomiage.aws_synthesize_speech(detect_text, filepath)
        # 音声データを再生
        subprocess.check_call('aplay -D plughw:0 {}'.format(filepath), shell=True)
        
        self.infomessage()


    def imageCB(self, msg):
        # カメラ画像を受け取る
        self.image = CvBridge().imgmsg_to_cv2(msg, "bgr8")
        cv2.imshow('Camera', cv2.resize(self.image, dsize=None, fx=0.75, fy=0.75))
        # キー判定をする
        key = cv2.waitKey(1)
        if key == ord('s'):
            self.enable_process = 1
        if key == ord('e'):
            self.enable_process = 2


    def infomessage(self):
        print("=======================================================================")
        print("文字読み上げシステム")
        print("  - カメラウィンドウを選択した状態で[s]キーを押すと読み上げ開始")
        print("  - [e]キーを押すと終了します。")
        print("=======================================================================")


    def run(self):
        # 案内用のメッセージを表示
        self.infomessage()
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if self.enable_process == 1:
                self.enable_process = 0
                self.process()
            if self.enable_process == 2:
                self.enable_process = 0
                print("３秒後にプログラムを終了します。")
                rospy.sleep(3)
                sys.exit(0)
            rate.sleep()

if __name__ == '__main__':
    # ノードを宣言
    rospy.init_node('yomiage_node')
    Yomiage().run()
