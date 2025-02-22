import tensorflow as tf
import tensorflow_hub as hub
import librosa
import matplotlib.pyplot as plt
import numpy as np
import imageio_ffmpeg as ffmpeg
import subprocess
import scipy.signal as signal
import noisereduce as nr
from collections import Counter
import csv

sampleRate = 16000

def class_names_from_csv(class_map_csv_text):
  """Returns list of class names corresponding to score vector."""
  class_names = []
  with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      class_names.append(row['display_name'])

  return class_names


def extract_audio(video_path, audio_path):
    """ FFmpeg을 사용하여 동영상에서 오디오 추출 """
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg_path, "-i", video_path, "-acodec", "pcm_s16le", "-ar", f"{sampleRate}", "-ac", "1", audio_path, "-y"]
    subprocess.run(command, shell=True)


def detect_music_sections(audio_path, min_group_duration = 60):
    """ YAMNet 모델을 사용하여 음악 구간 탐지 """
    model = hub.load("https://tfhub.dev/google/yamnet/1")

    y, sr = librosa.load(audio_path, sr=sampleRate)
    y = reduce_noise(y, sampleRate)
    y = apply_bandpass_filter(y, sampleRate)
    y = np.array(y, dtype=np.float32)

    duration = len(y)/sampleRate
    print(f'Sample rate: {sampleRate} Hz')
    print(f'Total duration: {duration:.2f}s')

    scores, embeddings, spectrogram = model(y)

    speech_classes = [0]
    speech_prob = np.sum(scores.numpy()[:, speech_classes], axis=1)

    music_classes  = [132,261]
    music_prob = np.mean(scores.numpy()[:, music_classes], axis=1)

    combined_prob = np.maximum(music_prob - speech_prob, 0)

    window_size = 10
    music_prob_smoothed = np.convolve(combined_prob, np.ones(window_size)/window_size, mode='valid')
    print(f"music_prob_smoothed count: {len(music_prob_smoothed)}")

    frame_duration = duration / len(music_prob_smoothed)
    print(f"frame_duration: {frame_duration}")

    # 동적 임계값
    dynamic_threshold = np.mean(music_prob_smoothed)
    print(f"dynamic_threshold: {dynamic_threshold}")
    plot_music_probability(music_prob_smoothed, frame_duration, dynamic_threshold)

    music_sections = np.where(music_prob_smoothed >= dynamic_threshold)[0]
    music_times_in_seconds = [index * frame_duration for index in music_sections]

    # min_duration 이상인 구간 제거
    filtered_music_times = []
    prev_time = None
    for time in music_times_in_seconds:
        if prev_time is not None and (time - prev_time < frame_duration * 3):
            filtered_music_times.append(time)
        prev_time = time

    # 인접한 값들을 그룹화하여 2차원 배열로 변환
    grouped_music_times = []
    current_group = []
    for time in filtered_music_times:
        if not current_group:
            current_group.append(time)
        elif (time - current_group[-1]) < min_group_duration * 0.5:
            current_group.append(time)
        else:
            grouped_music_times.append(current_group)
            current_group = [time]
    if current_group:
        grouped_music_times.append(current_group)

    # min_group_duration 이상인 구간만 포함
    final_grouped_music_times = [group for group in grouped_music_times if (max(group) - min(group)) > min_group_duration]
    return final_grouped_music_times


def find_music_segments(video_file):
    """ 동영상에서 음악 구간을 탐지하고 반환 """
    audio_path = "C:/Users/beomjk/Downloads/temp_audio.wav"
    extract_audio(video_file, audio_path)
    return detect_music_sections(audio_path)


def reduce_noise(y, sr):
    """ 배경 소음 제거 """
    auto_prop_decrease = detect_auto_prop_decrease(y)
    return nr.reduce_noise(y=y, sr=sr, prop_decrease=auto_prop_decrease, stationary=True)


def detect_auto_prop_decrease(y):
    """ 노이즈 레벨(SNR)에 따라 prop_decrease 값 자동 조정 """
    noise_level = np.mean(np.abs(y))  # 오디오 신호의 평균 진폭 계산
    print(f"noise_level: {noise_level}")
    if noise_level < 0.01:  # 매우 조용한 오디오
        return 0.2
    elif noise_level < 0.05:  # 중간 정도 소음
        return 0.4
    else:  # 노이즈가 심한 경우
        return 0.6
    

def apply_bandpass_filter(y, sr, lowcut=200, highcut=8000, order=5):
    """ 저주파(200Hz 이하) & 고주파(8kHz 이상) 제거 """
     # 필터 계수 계산 (Butterworth 필터)
    nyquist = 0.5 * sr  # 나이퀴스트 주파수 (샘플링 주파수의 절반)

    if highcut >= nyquist:
        highcut = nyquist - 1
    
    low = lowcut / nyquist
    high = highcut / nyquist

    b, a = signal.butter(order, [low, high], btype='band')  # Bandpass 필터 생성

    # 필터 적용
    return signal.lfilter(b, a, y)


def plot_music_probability(music_prob, frame_duration, threshold):
    """ music_prob을 시간에 따라 그래프로 시각화 """
    # X축: 시간(초)
    time_axis = np.arange(len(music_prob)) * frame_duration
    # 그래프 그리기
    plt.figure(figsize=(12, 5))
    plt.plot(time_axis, music_prob, label="Music Probability", color="b", alpha=0.7)
    plt.axhline(y=threshold, color='r', linestyle='--', label=f"Threshold ({threshold})")  # 임계값 표시
    plt.xlabel("Time (seconds)")
    plt.ylabel("Probability of Music")
    plt.title("Music Probability over Time")
    plt.legend()
    plt.grid(True)
    plt.show()



# 실행 예제
video_file = "C:/Users/beomjk/Downloads/videoplayback.mp4"
section = find_music_segments(video_file)
for idx, range in enumerate(section):
    print(f"music{idx + 1}:", min(range) , "~", max(range))
