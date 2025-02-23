# 프로젝트 환경 설정

Python 프로젝트를 시작하기 위한 가상 환경 설정 및 의존성 설치 방법을 안내합니다.

## 가상 환경 생성
```bash
python -m venv .venv
```

## 가상 환경 활성화
```bash
#cmd
.venv\Scripts\activate

#powershell
.venv\Scripts\Activate.ps1

#bash
source .venv/bin/activate
```

## 비활성화
```bash
deactivate
```


## 의존성 설치
```bash
pip install --upgrade pip

pip install -r requirements.txt
```
## 의존성 내보내기
```bash
pip freeze > requirements.txt
```

## FastAPI 개발 실행
```bash
# ./server
fastapi dev main.py
```