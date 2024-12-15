#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from audio_common_msgs.msg import AudioData
from cv_bridge import CvBridge
import cv2
import wave
import subprocess
import threading
import os

class VideoAudioRecorder:
    def __init__(self):
        rospy.init_node('video_audio_recorder', anonymous=True)

        # 訂閱相機和音頻主題
        self.bridge = CvBridge()
        self.frame = None
        rospy.Subscriber('/camera', Image, self.image_callback)
        rospy.Subscriber('/audio', AudioData, self.audio_callback)

        # 設置錄製參數
        self.fps = rospy.get_param("fps", 30)
        self.video_filename = rospy.get_param("video_filename", "output.avi")
        self.audio_filename = rospy.get_param("audio_filename", "output.wav")
        self.output_filename = rospy.get_param("output_filename", "output.mp4")

        # 初始化視頻錄製
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.video_filename, self.fourcc, self.fps, (640, 480))

        # 初始化音頻錄製
        self.audio_frames = []
        self.audio_rate = 16000  # 16 kHz

        # 開啟錄製
        self.recording = True

    def image_callback(self, msg):
        # 將 ROS Image 消息轉換為 OpenCV 格式
        self.frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def audio_callback(self, msg):
        # 收集音頻數據
        self.audio_frames.append(msg.data)

    def record_video(self):
        # 持續錄製視頻
        rate = rospy.Rate(self.fps)
        while not rospy.is_shutdown() and self.recording:
            if self.frame is not None:
                self.out.write(self.frame)
            rate.sleep()

    def save_audio(self):
        # 將音頻數據保存為 WAV 文件
        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 每個采樣點的字節數 (16位 = 2字節)
            wf.setframerate(self.audio_rate)
            wf.writeframes(b''.join(self.audio_frames))

    def stop_recording(self):
        # 停止錄製
        self.recording = False
        self.out.release()
        rospy.loginfo("Video recording stopped.")
        self.save_audio()
        rospy.loginfo("Audio recording saved.")

        # 使用 ffmpeg 合併音視頻
        cmd = f"ffmpeg -i {self.video_filename} -i {self.audio_filename} -c:v libx264 -c:a aac -strict experimental {self.output_filename}"
        subprocess.call(cmd, shell=True)
        rospy.loginfo(f"Output file saved as {self.output_filename}")

    def run(self):
        video_thread = threading.Thread(target=self.record_video)
        video_thread.start()
        rospy.on_shutdown(self.stop_recording)
        rospy.spin()


if __name__ == '__main__':
    recorder = VideoAudioRecorder()
    recorder.run()
