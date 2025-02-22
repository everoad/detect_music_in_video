import tensorflow_hub as hub
import librosa
import numpy as np

# YAMNet 모델 로드
model = hub.load("https://tfhub.dev/google/yamnet/1")

def detect_music_sections(audio_path):
    # 오디오 로드
    y, sr = librosa.load(audio_path, sr=16000)
    
    # 모델 적용
    scores, embeddings, spectrogram = model(y)
    
    # "music" 클래스 (YAMNet의 53번 인덱스)
    music_prob = scores.numpy()[:, 53]
    
    # 음악 구간 찾기 (확률 0.5 이상인 부분)
    music_sections = np.where(music_prob > 0.3)[0]

    return music_sections

# 사용 예제
music_times = detect_music_sections("C:/Users/beomjk/Downloads/output.wav")
print("Detected music sections:", music_times)