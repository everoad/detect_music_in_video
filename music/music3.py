import tensorflow as tf
import tensorflow_hub as hub
import librosa
import matplotlib.pyplot as plt
import numpy as np
import imageio_ffmpeg as ffmpeg
import subprocess
import scipy.signal as signal
import noisereduce as nr
import csv
from scipy.ndimage import gaussian_filter1d

sampleRate = 16000

def classes_from_csv(class_map_csv_text):
  """Returns list of class names corresponding to score vector."""
  class_names = []
  with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      class_names.append([row['display_name'], int(row['index'])])

  return class_names


def extract_audio(video_path, audio_path):
    """ FFmpeg을 사용하여 동영상에서 오디오 추출 """
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg_path, "-i", video_path, "-acodec", "pcm_s16le", "-ar", f"{sampleRate}", "-ac", "1", audio_path, "-y"]
    subprocess.run(command, shell=True)


def group_and_filter_music_times(music_times, min_term_duration):
    grouped_music_times = []
    current_group = []
    for time in music_times:
        if not current_group:
            current_group.append(time)
        elif (time - current_group[-1]) < min_term_duration:
            current_group.append(time)
        else:
            grouped_music_times.append(current_group)
            current_group = [time]
    if current_group:
        grouped_music_times.append(current_group)

    filtered_music_times = [
        group for group in grouped_music_times
        if (max(group) - min(group)) >= (min_term_duration * 0.5)
    ]

    return filtered_music_times

def iterative_group_and_filter(music_times, min_durations):
    """
    min_durations 리스트에 있는 값을 순차적으로 적용하면서 음악 시간을 그룹화하고 필터링한다.
    """
    grouped_music_times = music_times
    for index, min_duration in enumerate(min_durations):
        if (index == 0):
            grouped_music_times = group_and_filter_music_times(grouped_music_times, min_duration)
        else:
            grouped_music_times = group_and_filter_music_times(sum(grouped_music_times, []), min_duration)

    return grouped_music_times

def detect_music_sections(audio_path):
    """ YAMNet 모델을 사용하여 음악 구간 탐지 """
    model = hub.load("https://tfhub.dev/google/yamnet/1")

    class_map_path = model.class_map_path().numpy()
    classes = classes_from_csv(class_map_path)
    music_class_index = [index for name, index in classes if "Music" in name][0]
    print(f"Music class index: {music_class_index}")

    y, sr = librosa.load(audio_path, sr=sampleRate)
    y = reduce_noise(y, sampleRate)
    y = apply_bandpass_filter(y, sampleRate)
    y = np.array(y, dtype=np.float32)
    
    duration = len(y)/sampleRate
    scores, embeddings, spectrogram = model(y)

    # Music 클래스의 확률만 추출
    music_prob = scores.numpy()[:, music_class_index]
    music_prob_smoothed = gaussian_filter1d(music_prob, sigma=3)

    dynamic_threshold = np.mean(music_prob_smoothed)
    # 프레임별 가장 높은 확률의 클래스 인덱스 찾기 (Top-1)
    top_class_indices = np.argmax(scores.numpy(), axis=1)

    frame_duration = duration / len(top_class_indices)
    timestamps = np.array([i * frame_duration for i in range(len(scores))])

    music_indices = np.where(top_class_indices == music_class_index)[0]
    music_times_in_seconds = timestamps[music_indices]

    plot_music_probability(music_prob_smoothed, frame_duration, dynamic_threshold)
    # min_duration 이상인 구간 제거
    filtered_music_times = []
    prev_time = None
    for time in music_times_in_seconds:
        if prev_time is not None and (time - prev_time < frame_duration * 3):
            filtered_music_times.append(time)
        prev_time = time

    # 인접한 값들을 그룹화하여 2차원 배열로 변환
    min_term_durations = [5, 10, 15]
    grouped_music_times = iterative_group_and_filter(filtered_music_times, min_term_durations)

    # 각 구간의 평균 Music 확률 계산
    music_section_averages = []
    for group in grouped_music_times:
        start_time, end_time = min(group), max(group)
        
        # 해당 시간 범위의 인덱스 찾기
        section_indices = np.where((timestamps >= start_time) & (timestamps <= end_time))[0]
        
        if len(section_indices) > 0:
            avg_music_score = np.mean(music_prob_smoothed[section_indices])  # 평균 Music 확률 계산
        else:
            avg_music_score = 0  # 만약 구간 내 데이터가 없으면 0 처리
        
        music_section_averages.append(avg_music_score)

    for group, avg_score in zip(grouped_music_times, music_section_averages):
        print(f"{min(group):.1f} ~ {max(group):.1f}, {avg_score:.2f}")

    min_group_duration = 60
    #🎯 30초 이상 & 평균 Music 확률이 0.35 이상인 구간만 포함
    final_grouped_music_times = [
        group for group, avg_score in zip(grouped_music_times, music_section_averages)
        if (max(group) - min(group)) > min_group_duration and avg_score >= dynamic_threshold
    ]
    return final_grouped_music_times


def find_music_segments(video_file):
    """ 동영상에서 음악 구간을 탐지하고 반환 """
    audio_path = "C:/Users/kbj/Downloads/temp_audio.wav"
    extract_audio(video_file, audio_path)
    return detect_music_sections(audio_path)


def reduce_noise(y, sr):
    """ 배경 소음 제거 """
    auto_prop_decrease = detect_auto_prop_decrease(y)
    return nr.reduce_noise(y=y, sr=sr, prop_decrease=auto_prop_decrease, stationary=True)


def detect_auto_prop_decrease(y):
    """ 노이즈 레벨(SNR)에 따라 prop_decrease 값 자동 조정 """
    noise_level = np.mean(np.abs(y))  # 오디오 신호의 평균 진폭 계산
    print(f"Noise level: {noise_level}")
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
video_file = "C:/Users/kbj/Downloads/videoplayback2.mp4"
section = find_music_segments(video_file)
for idx, range in enumerate(section):
    print(f"music {idx + 1}: {min(range)} ~ {max(range)}")