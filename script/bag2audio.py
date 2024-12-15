#!/usr/bin/env python3
import io

import rosbag
import wave
import numpy as np
from pydub import AudioSegment
from noisereduce import reduce_noise

def extract_audio_from_bag(bag_file, topic_name, output_wav):
    # open rosbag
    bag = rosbag.Bag(bag_file, 'r')
    audio_data = b""

    # extract /audio data
    for topic, msg, t in bag.read_messages(topics=[topic_name]):
        audio_data += msg.data
    bag.close()

    # use pydub decode MP3 to PCM
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
    sample_rate = audio_segment.frame_rate

    # filter noise
    reduced_noise = reduce_noise(y=samples, sr=sample_rate)

    # save as WAV file
    with wave.open(output_wav, 'wb') as wf:
        wf.setnchannels(audio_segment.channels)
        wf.setsampwidth(audio_segment.sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(reduced_noise.astype(np.int16).tobytes())

    print(f"Audio extracted and saved to {output_wav}")


if __name__ == "__main__":
    # set parameters
    bag_file = "/home/rg413/makeVideo/bags/test.bag"  # rosbag file path
    topic_name = "/audio"   # audio topic name
    output_wav = "output.wav"  # output path

    extract_audio_from_bag(bag_file, topic_name, output_wav)
