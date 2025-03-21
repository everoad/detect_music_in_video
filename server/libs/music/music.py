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
import os
from scipy.ndimage import gaussian_filter1d
import itertools
# from log.log_config import logger

sample_rate = 16000

# 내부 연산(예: 행렬 곱셈)에서 사용할 스레드 수 제한
tf.config.threading.set_intra_op_parallelism_threads(2)
# 연산 간 병렬 처리를 위한 스레드 수 제한
tf.config.threading.set_inter_op_parallelism_threads(2)

def classes_from_csv(class_map_csv_text):
    """ CSV 파일에서 클래스 이름을 읽어와서 반환 """
    class_names = []
    with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_names.append([row['display_name'], int(row['index'])])

    return class_names


def file_exists(file_path):
    """파일이 해당 경로에 존재하는지 확인"""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def extract_audio(video_path, audio_path):
    if file_exists(audio_path):
        return
    
    """ FFmpeg을 사용하여 동영상에서 오디오 추출 """
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg_path, "-i", video_path, "-acodec", "pcm_s16le", "-ar", f"{sample_rate}", "-ac", "1", audio_path, "-y"]
    subprocess.run(command, shell=True)



def download_in_chunks(url, output_file, chunk_size="3M"):
    """
    yt-dlp를 사용하여 4MB 단위로 영상을 다운로드하는 함수

    :param url: 다운로드할 영상 URL
    :param output_file: 최종 저장될 파일명 (예: "output.mp4")
    :param chunk_size: 다운로드할 청크 크기 (기본값: 4MB)
    """
    
    if file_exists(output_file):
        return

    temp_file = output_file + ".part"
    
    print(f"다운로드 시작... {url}")
    
    command = [
        "yt-dlp",
        "--no-part",  # 임시 파일 확장자 사용 안 함
        "--http-chunk-size", chunk_size,  # 4MB 단위
        "--output", temp_file,  # 임시 저장 파일
        url,
    ]
    subprocess.run(command, shell=True, check=True, text=True)
    
    print("다운로드 완료...")


def extract_audio_from_url(video_url: str, video_output_path: str, audio_output_path: str):
    try:        
        download_in_chunks(url=video_url, output_file=video_output_path)
        
        command = [
            'ffmpeg',
            "-i", video_output_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", str(sample_rate),
            "-ac", "1",
            audio_output_path,
            "-y"
        ]
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print(f"❌ Error extract audio: {e}")


def group_and_filter_music_times(
    music_times, min_term_duration, timestamps, 
    music_scores, singing_scores, 
    music_threshold, singing_threshold
):
    """ 음악 시간을 그룹화하고 필터링 """
    exception_high_factor = 1.5
    exception_row_factor = 0.5
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

    
    # 그룹별로 평균 확률 계산
    filtered_music_times = []
    for group in grouped_music_times:
        start_time, end_time = min(group), max(group)
        diff = (end_time - start_time)
        section_indices = np.where((timestamps >= start_time) & (timestamps <= end_time))[0]
        
        avg_score = []
        if len(section_indices) > 0:
            avg_score = [
                np.mean(music_scores[section_indices]),  # 평균 Music 확률 계산
                np.mean(singing_scores[section_indices]) # 평균 Singing 확률 계산
            ]
        else:
            avg_score = [0, 0]

        # print(f"구간 점수: {min_term_duration}, {start_time:.0f} ~ {end_time:.0f}, {(diff/len(group)):.3f}, {avg_score[0]:.3f}, {avg_score[1]:.3f}")
        # 음악 및 노래 확률이 임계값 이상이거나, 그룹의 평균 확률이 일정 범위 내에 있을 때만 유효한 음악 구간으로 간주
        if (end_time - start_time) >= (min_term_duration * 0.5) and diff/len(group) > 0 and diff/len(group) <= 1 and (
                (avg_score[0] >= music_threshold and avg_score[1] >= singing_threshold) or
                (avg_score[0] >= music_threshold * exception_high_factor and avg_score[1] >= singing_threshold * exception_row_factor) or
                (avg_score[0] >= music_threshold * exception_row_factor and avg_score[1] >= singing_threshold * exception_high_factor)):
            filtered_music_times.append(group)
    
    return filtered_music_times

def iterative_group_and_filter(music_times, min_durations, timestamps, music_prob, singing_prob, music_threshold, singing_threshold):
    """
    min_durations 리스트에 있는 값을 순차적으로 적용하면서 음악 시간을 그룹화하고 필터링한다.
    """
    grouped_music_times = music_times
    for index, min_duration in enumerate(min_durations):
        if (index == 0):
            grouped_music_times = group_and_filter_music_times(
                grouped_music_times, min_duration, timestamps, 
                music_prob, singing_prob,
                music_threshold, singing_threshold
            )
        else:
            flattened = list(itertools.chain.from_iterable(grouped_music_times))
            grouped_music_times = group_and_filter_music_times(
                flattened, min_duration, timestamps, 
                music_prob, singing_prob,
                music_threshold, singing_threshold
            )

    return grouped_music_times


def detect_music_sections(audio_path):
    """ YAMNet 모델을 사용하여 음악 구간 탐지 """
    print("오디오 분석 시작...")
    model = hub.load("https://tfhub.dev/google/yamnet/1")

    class_map_path = model.class_map_path().numpy()
    classes = classes_from_csv(class_map_path)
    music_class_index = [index for name, index in classes if "Music" in name][0]
    print(f"Music 클래스: {music_class_index}")
    singing_class_index = [index for name, index in classes if "Singing" in name][0]
    print(f"Singing 클래스: {singing_class_index}")
    speech_class_index = [index for name, index in classes if "Speech" in name][0]
    print(f"Speech 클래스: {speech_class_index}")

    y, sr = librosa.load(audio_path, sr=sample_rate)
    y = reduce_noise_chunked(y, sample_rate, chunk_duration=10)
    y = apply_bandpass_filter(y, sample_rate)
    y = np.array(y, dtype=np.float32)
    print(f"오디오 파일 크기: {len(y)}")
    
    print("청크 단위로 모델 분석 시작...")
    chunk_duration = 9.6
    chunk_samples = int(chunk_duration * sample_rate)     # 9.6초에 해당하는 샘플 수 (예: 153600)

    all_scores_list = []
    all_embeddings_list = []
    for start in range(0, len(y), chunk_samples):
        # end = start + chunk_samples
        end = min(start + chunk_samples, len(y))
        chunk = y[start:end]
        chunk_scores, chunk_embeddings, chunk_spectrogram = model(chunk)
        all_scores_list.append(chunk_scores.numpy())
        all_embeddings_list.append(chunk_embeddings.numpy())
        
    # 청크별 결과를 이어 붙여 전체 프레임 배열 생성
    scores_np = np.concatenate(all_scores_list, axis=0)
    embeddings_np = np.concatenate(all_embeddings_list, axis=0)
    print(f"모델 분석 완료. {len(scores_np)}")
    
    # Musics, Singing 클래스의 확률만 추출
    sigma = 3
    smoothed_scores = np.apply_along_axis(gaussian_filter1d, 0, scores_np, sigma)
    music_scores = smoothed_scores[:, music_class_index]
    singing_scores = smoothed_scores[:, singing_class_index]
    speech_scores = smoothed_scores[:, speech_class_index]

    # 동적 임계값
    music_threshold = np.mean(music_scores)
    singing_threshold = np.mean(singing_scores)
    speech_threshold = np.mean(speech_scores)
    print(f"Music 동적 임계값: {music_threshold}")
    print(f"Singing 동적 임계값: {singing_threshold}")
    print(f"Speech 동적 임계값: {speech_threshold}")
    
    # 프레임별 가장 높은 확률의 클래스 인덱스 찾기 (Top-1)
    top_class_indices = np.argmax(smoothed_scores, axis=1)
    
    duration = len(y)/sample_rate
    print(f"오디오 길이: {duration:.0f} 초")
    frame_duration = duration / len(top_class_indices)
    print(f"프레임 길이: {frame_duration:.3f} 초")
    timestamps = np.arange(len(top_class_indices)) * frame_duration

    # music 또는 singing이 최고 확률인 프레임 인덱스를 선택
    music_indices = np.where(
        (top_class_indices == music_class_index) | (top_class_indices == singing_class_index)
    )[0]
    music_times = timestamps[music_indices]
    
    # plot_music_probability(music_scores, singing_scores, speech_scores, music_threshold, singing_threshold, speech_threshold, frame_duration)
    # return

    # min_duration 이상인 구간 제거
    diff = np.diff(music_times)
    mask = diff < (frame_duration * 5)
    # 첫 번째 값은 조건 비교에서 제외되므로, mask를 prepend False하여 동일한 결과를 얻음
    filtered_music_times = music_times[np.concatenate(([False], mask))]

    # 인접한 값들을 그룹화하여 2차원 배열로 변환
    min_durations = [frame_duration * 15, frame_duration * 20, frame_duration * 25, frame_duration * 30]
    grouped_music_times = iterative_group_and_filter(
        filtered_music_times, min_durations, timestamps, 
        music_scores, singing_scores,
        music_threshold, singing_threshold
    )

    # 최소 노래 길이 필터링
    min_music_duration = 60
    final_music_sections = [
        group for group in grouped_music_times
        if (max(group) - min(group)) > min_music_duration
    ]
    print("오디오 분석 완료...")
    return final_music_sections

def find_music_segments(video_path, audio_path):
    """ 동영상에서 음악 구간을 탐지하고 반환 """
    extract_audio(video_path, audio_path)
    return detect_music_sections(audio_path)


def reduce_noise_chunked(y, sr, chunk_duration=10):
    """ 청크 단위로 오디오 노이즈 제거 수행 (기본 청크 길이: 10초) """
    print("노이즈 제거 시작 (청크 단위)...")
    chunk_size = int(chunk_duration * sr)  # 청크당 샘플 수 계산
    auto_prop_decrease = detect_auto_prop_decrease(y)
    reduced_audio = np.empty_like(y)
    # 청크별로 노이즈 제거 처리
    for start in range(0, len(y), chunk_size):
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


def plot_music_probability(music_prob, singing_prob, speech_prob, music_thres, singing_thres, speech_thres, frame_duration):
    """ music_prob을 시간에 따라 그래프로 시각화 """
    # X축: 시간(초)
    time_axis = np.arange(len(music_prob)) * frame_duration
    # 그래프 그리기
    plt.figure(figsize=(12, 5))
    plt.plot(time_axis, music_prob, label="Music Probability", color="b", alpha=0.7)
    plt.plot(time_axis, singing_prob, label="Singing Probability", color="r", alpha=0.7)
    plt.plot(time_axis, speech_prob, label="Speech Probability", color="g", alpha=0.7)
    plt.axhline(y=music_thres, color='b', linestyle='--', label=f"Threshold ({music_thres})")  # 임계값 표시
    plt.axhline(y=singing_thres, color='r', linestyle='--', label=f"Threshold ({singing_thres})")  # 임계값 표시
    plt.axhline(y=speech_thres, color='g', linestyle='--', label=f"Threshold ({speech_thres})")  # 임계값 표시
    plt.xlabel("Time (seconds)")
    plt.ylabel("Probability of Music")
    plt.title("Music Probability over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


video_path = "D:/workspace/detect_music/client/public/videos/6015286.mp4"
audio_path = "C:/Users/kbj/Downloads/6015286.wav"
segments = find_music_segments(video_path, audio_path)

# if segments:
#     for idx, segment in enumerate(segments):
#         print(f"{idx + 1}. {min(segment)} ~ {max(segment)}")