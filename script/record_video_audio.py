#!/usr/bin/env python3

import rospy
import subprocess
import os
import argparse


# Import the function from the existing scripts
from bag2audio import extract_audio_from_bag
from bag2video import RosVideoWriter


def generate_video_from_bag(bag_file, audio_topic, image_topic, output_video_file, output_audio_file, final_file, fps=30, rate=1):
    # Step 1: Extract audio from the ROS bag
    print(f"Extracting audio from bag file: {bag_file}")
    extract_audio_from_bag(bag_file, audio_topic, output_audio_file)

    # Step 2: Create video from the image topic in the ROS bag
    print(f"Creating video from bag file: {bag_file}")
    videowriter = RosVideoWriter(fps=fps, rate=rate, topic=image_topic, output_filename=output_video_file)
    videowriter.addBag(bag_file)
    repaired_video_file = "repaired_video.mp4"
    cmd = [
        "ffmpeg", "-i", output_video_file, "-c", "copy",
        "-movflags", "+faststart", repaired_video_file
    ]
    subprocess.run(cmd)

    # Step 3: Combine audio and video using ffmpeg
    print(f"Combining video and audio into {final_file}")
    combine_audio_and_video(output_video_file, output_audio_file, final_file)


def combine_audio_and_video(video_file, audio_file, final_file = "final.mp4"):
    command = [
        "ffmpeg", "-i", video_file, "-i", audio_file,
        "-c:v", "copy", "-strict", "experimental", final_file
    ]
    subprocess.run(command)
    print(f"Final video saved as {final_file}")

def setArg():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-b", "--bag",help="bag path", default="/path/to/your/rosbag.bag")
    argParser.add_argument("-a", "--audio", help="audio topic", default="/audio")
    argParser.add_argument("-i", "--image", help="image topic", default="/usb_cam/image_raw")
    argParser.add_argument("-v", "--video", help="output video file", default="video.mp4")
    argParser.add_argument("-s", "--sound", help="output sound file", default="sound.wav")
    argParser.add_argument("-f", "--final", help="final output file", default="final.mp4")
    args = argParser.parse_args()
    return args

if __name__ == "__main__":
    args = setArg()

    # generate_video_from_bag(bag_file = args., audio_topic, image_topic, output_video_file, output_audio_file)
    generate_video_from_bag(bag_file = args.bag, 
                            audio_topic = args.audio, 
                            image_topic = args.image, 
                            output_video_file = args.video,
                            output_audio_file = args.sound,
                            final_file = args.final)
    
    # combine_audio_and_video(args.video, args.sound, args.final)   

