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
import json
import itertools
from sklearn.cluster import DBSCAN

sample_rate = 16000

# 내부 연산(예: 행렬 곱셈)에서 사용할 스레드 수 제한
tf.config.threading.set_intra_op_parallelism_threads(2)
# 연산 간 병렬 처리를 위한 스레드 수 제한
tf.config.threading.set_inter_op_parallelism_threads(2)

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
    command = [ffmpeg_path, "-i", video_path, "-acodec", "pcm_s16le", "-ar", f"{sample_rate}", "-ac", "1", audio_path, "-y"]
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

    filtered_music_times = []
    for group in grouped_music_times:
        start_time, end_time = min(group), max(group)
        if (end_time - start_time) >= (min_term_duration * 0.5) and (end_time - start_time)/len(group) <= 1:
            print(f"구간 점수: {((end_time - start_time)/len(group)):.3f}")
            filtered_music_times.append(group)
    
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
            flattened = list(itertools.chain.from_iterable(grouped_music_times))
            grouped_music_times = group_and_filter_music_times(flattened, min_duration)

    return grouped_music_times


def detect_music_sections(audio_path):
    """ YAMNet 모델을 사용하여 음악 구간 탐지 """
    model = hub.load("https://tfhub.dev/google/yamnet/1")

    class_map_path = model.class_map_path().numpy()
    classes = classes_from_csv(class_map_path)
    music_class_index = [index for name, index in classes if "Music" in name][0]
    print(f"Music class index: {music_class_index}")
    singing_class_index = [index for name, index in classes if "Singing" in name][0]
    print(f"Singing class index: {singing_class_index}")

    y, sr = librosa.load(audio_path, sr=sample_rate)
    # y = reduce_noise(y, sampleRate)
    y = reduce_noise_chunked(y, sample_rate, chunk_duration=10)
    y = apply_bandpass_filter(y, sample_rate)
    y = np.array(y, dtype=np.float32)
    

    print("청크 단위로 모델 분석 시작...")
    chunk_duration = 10  # 초
    chunk_samples = int(chunk_duration * sample_rate)
    all_scores = []
    for start in segment(0, len(y), chunk_samples):
        end = start + chunk_samples
        chunk = y[start:end]
        # 마지막 청크가 10초보다 짧으면 0 패딩
        if len(chunk) < chunk_samples:
            chunk = np.pad(chunk, (0, chunk_samples - len(chunk)), mode='constant')
        chunk_scores, chunk_embeddings, chunk_spectrogram = model(chunk)
        all_scores.append(chunk_scores)
    
     # 청크별 결과 결합
    scores_np = np.concatenate([s.numpy() for s in all_scores], axis=0)
    print("모델 분석 완료.")
    
    # Musics, Singing 클래스의 확률만 추출
    music_prob_smoothed = gaussian_filter1d(scores_np[:, music_class_index], sigma=3)
    singing_prob_smoothed = gaussian_filter1d(scores_np[:, singing_class_index], sigma=3)

    # 동적 임계값
    music_dynamic_threshold = np.mean(music_prob_smoothed)
    singing_dynamic_threshold = np.mean(singing_prob_smoothed)
    print(f"Music 동적 임계값: {music_dynamic_threshold}")
    print(f"Singing 동적 임계값: {singing_dynamic_threshold}")
    
    # 프레임별 가장 높은 확률의 클래스 인덱스 찾기 (Top-1)
    top_class_indices = np.argmax(scores_np, axis=1)

    duration = len(y)/sample_rate
    frame_duration = duration / len(top_class_indices)
    timestamps = np.arange(len(top_class_indices)) * frame_duration

    # music 또는 singing이 최고 확률인 프레임 인덱스를 선택
    music_or_singing_indices = np.where(
        (top_class_indices == music_class_index) | (top_class_indices == singing_class_index)
    )[0]
    music_or_singing_times = timestamps[music_or_singing_indices]

    # plot_music_probability(music_prob_smoothed, frame_duration, dynamic_threshold)

    # min_duration 이상인 구간 제거
    diff = np.diff(music_or_singing_times)
    mask = diff < (frame_duration * 5)
    # 첫 번째 값은 조건 비교에서 제외되므로, mask를 prepend False하여 동일한 결과를 얻음
    filtered_music_or_singing_times = music_or_singing_times[np.concatenate(([False], mask))]

    # 인접한 값들을 그룹화하여 2차원 배열로 변환
    min_term_durations = [7.5, 10, 15]
    grouped_music_or_singing_times = iterative_group_and_filter(filtered_music_or_singing_times, min_term_durations)

    # 각 구간의 평균 Music 확률 계산
    section_averages = []
    for group in grouped_music_or_singing_times:
        start_time, end_time = min(group), max(group)
        
        # 해당 시간 범위의 인덱스 찾기
        section_indices = np.where((timestamps >= start_time) & (timestamps <= end_time))[0]
        
        if len(section_indices) > 0:
            section_averages.append([
                np.mean(music_prob_smoothed[section_indices]),  # 평균 Music 확률 계산
                np.mean(singing_prob_smoothed[section_indices]) # 평균 Singing 확률 계산
            ])
        else:
            section_averages.append([0, 0])

    for group, avg_score in zip(grouped_music_or_singing_times, section_averages):
        start_time, end_time = min(group), max(group)
        group_size = len(group)
        print(f"최종 구간 점수: {start_time:.0f} ~ {end_time:.0f}, {(end_time - start_time):.0f}, {avg_score[0]:.2f}, {avg_score[1]:.2f}, {((end_time - start_time)/group_size):.2f}")


    exception_high_factor = 1.5
    exception_row_factor = 0.5
    min_group_duration = 60
    #🎯 30초 이상 & 평균 Music 확률이 0.35 이상인 구간만 포함
    final_grouped_music_times = [
        group for group, avg_score in zip(grouped_music_or_singing_times, section_averages)
        if (max(group) - min(group)) > min_group_duration and (
            (avg_score[0] >= music_dynamic_threshold and avg_score[1] >= singing_dynamic_threshold) or
            (avg_score[0] >= music_dynamic_threshold * exception_high_factor and avg_score[1] >= singing_dynamic_threshold * exception_row_factor) or
            (avg_score[0] >= music_dynamic_threshold * exception_row_factor and avg_score[1] >= singing_dynamic_threshold * exception_high_factor)
        )
    ]
    return final_grouped_music_times

def find_music_segments(video_file):
    """ 동영상에서 음악 구간을 탐지하고 반환 """
    audio_path = "C:/Users/kbj/Downloads/temp_audio2.wav"
    extract_audio(video_file, audio_path)
    return detect_music_sections(audio_path)


def reduce_noise(y, sr):
    """ 배경 소음 제거 """
    auto_prop_decrease = detect_auto_prop_decrease(y)
    return nr.reduce_noise(y=y, sr=sr, prop_decrease=auto_prop_decrease, stationary=True)

def reduce_noise_chunked(y, sr, chunk_duration=10):
    """ 청크 단위로 오디오 노이즈 제거 수행 (기본 청크 길이: 10초) """
    print("노이즈 제거 시작 (청크 단위)...")
    chunk_size = int(chunk_duration * sr)  # 청크당 샘플 수 계산
    auto_prop_decrease = detect_auto_prop_decrease(y)
    reduced_audio = np.empty_like(y)
    # 청크별로 노이즈 제거 처리
    for start in segment(0, len(y), chunk_size):
        end = min(start + chunk_size, len(y))
        chunk = y[start:end]
        reduced_chunk = nr.reduce_noise(y=chunk, sr=sr, prop_decrease=auto_prop_decrease, stationary=True)
        reduced_audio[start:end] = reduced_chunk
    print("노이즈 제거 완료.")
    return reduced_audio


def detect_auto_prop_decrease(y):
    """ 노이즈 레벨(SNR)에 따라 prop_decrease 값 자동 조정 """
    noise_level = np.mean(np.abs(y))  # 오디오 신호의 평균 진폭 계산
    print(f"노이즈 레벨: {noise_level}")
    if noise_level < 0.01:  # 매우 조용한 오디오
        return 0.2
    elif noise_level < 0.05:  # 중간 정도 소음
        return 0.4
    else:  # 노이즈가 심한 경우
        return 0.6
    

def apply_bandpass_filter(y, sr, lowcut=200, highcut=8000, order=5):
    """ 저주파(200Hz 이하) & 고주파(8kHz 이상) 제거 """
    print("밴드패스 필터 시작...")
    nyquist = 0.5 * sr
    if highcut >= nyquist:
        highcut = nyquist - 1
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype='band')
    result = signal.lfilter(b, a, y)
    print("밴드패스 필터 완료.")
    return result


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
video_file = "C:/Users/kbj/Downloads/videoplayback3.mp4"
segments = find_music_segments(video_file)

ranges = []
for index, segment in enumerate(segments):
    start_time, end_time = min(segment), max(segment)
    ranges.append({
        "start": start_time,  # 구간의 최소값
        "end": end_time     # 구간의 최대값
    })
    print(f"노래 {index + 1}: {start_time:.0f} ~ {end_time:.0f}")  # 원래 출력 유지

# JSON 파일로 저장
with open('ranges.json', 'w', encoding='utf-8') as f:
    json.dump(ranges, f, indent=2)

print("JSON file 'ranges.json' created successfully.")