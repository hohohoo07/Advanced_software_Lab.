# 심화전공실습 10주차: 비디오 처리와 객체 추적

Windows의 로컬 Python 3.11 또는 3.12와 터미널을 기준으로 합니다.
ZIP을 모두 풀고 해당 폴더에서 터미널을 여세요. 발표·별도 제출 활동은 없습니다.

## 더블클릭으로 실행

1. ZIP을 모두 압축 해제합니다.
2. SETUP.bat를 실행해 패키지를 설치합니다.
3. RUN_PRACTICE.bat를 실행하고 1~4번 메뉴를 선택합니다.

## 처음 실행

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe 01_read_video.py
.venv\Scripts\python.exe 02_frame_difference.py
.venv\Scripts\python.exe 03_background_subtraction.py
.venv\Scripts\python.exe 04_motion_tracking.py
```

화면이 나타나면 q 키로 종료합니다. 활성화 명령 없이 가상환경의 python.exe를 직접 사용하므로 PowerShell 실행 정책 변경이 필요 없습니다.

## 실습 내용

| 파일 | 실행 내용 |
|---|---|
| 01_read_video.py | 동영상 정보 출력과 순차 재생 |
| 02_frame_difference.py | 인접 프레임 차이, 이진화, 형태학적 연산 |
| 03_background_subtraction.py | MOG2 전경 분리, 그림자 후보 제외, 영역 검출 |
| 04_motion_tracking.py | 중심점 거리 연결, ID와 궤적 표시, AVI·CSV 저장 |
| common.py | 전체 알고리즘 구현; 매개변수·추적 클래스 확인 |

## 매개변수 바꾸기

```powershell
.venv\Scripts\python.exe 04_motion_tracking.py --min-area 1200
.venv\Scripts\python.exe 04_motion_tracking.py --max-distance 30
.venv\Scripts\python.exe 03_background_subtraction.py --history 50 --var-threshold 40
.venv\Scripts\python.exe 04_motion_tracking.py --video "C:\cv_week10\my_video.mp4"
```

한 번에 하나의 설정을 바꾸고 같은 구간의 결과를 비교하세요. 모든 입력은 가로 640픽셀로 크기 조정합니다. min-area는 이 처리 영상에서의 윤곽선 면적 기준이며, max-distance는 이 영상에서 프레임 사이의 픽셀 거리입니다. max-missed의 기본값은 10프레임이고 common.py의 생성자에서 변경합니다.

## 실행 결과

`04_motion_tracking.py` 실행 후 `output/tracking_result.avi`와 `output/tracks.csv`가 생성됩니다.
동일 이름의 이전 결과는 덮어씁니다. 비교하려면 먼저 파일명을 바꾸세요.
CSV에는 frame(0부터), time_s(영상 시각), track_id, cx, cy, x, y, w, h가 기록됩니다.
좌표는 원본 768×576 영상이 아니라 처리 영상 640×480 기준입니다.
처음 30프레임은 배경 적응을 위한 예시 구간으로 추적 결과를 기록하지 않습니다.
워밍업 길이 30은 수업용 설정이며, 모든 영상에서 안정된 배경을 보장하지 않습니다.

## 결과 해석

- 검출 대상은 움직이는 영역입니다. 사람인지 자동차인지를 분류하지 않습니다.
- 중심점은 바운딩박스의 중심입니다. 윤곽선의 무게중심과 다를 수 있습니다.
- 탐욕적 거리 연결은 교육용입니다. 교차·가림·영역 병합과 분할에서 ID가 바뀔 수 있습니다.
- 현재 보이는 상자 수는 사람 수와 다를 수 있습니다. 생성된 ID 수 역시 순방문자 수가 아닙니다.
- 정지한 대상은 시간이 지나 배경으로 흡수될 수 있습니다. 고정 카메라가 기본 전제입니다.
- CSV의 time_s는 프레임 번호/원본 FPS로 계산한 영상 시각입니다. 처리 속도 측정값이 아닙니다.

## 오류 해결

- `No module named cv2`: 위 가상환경 python.exe로 requirements.txt를 설치했는지 확인합니다.
- `imshow` 오류: 이 실습은 로컬 Windows 창을 사용합니다. opencv-python-headless만 설치한 환경에서는 창이 표시되지 않습니다. 새 가상환경에 opencv-python을 설치하세요.
- 영상 열기 실패: ZIP을 모두 풀었는지, data/vtest.avi가 있는지 확인합니다.
- 동영상 저장 실패: 저장 폴더 권한과 코덱을 확인합니다. 기본 저장 형식은 MJPG/AVI입니다.
- 노트북·원격 환경에서 창 없이 실행하려면 `--no-gui`를 붙이세요. 추적 영상·CSV는 그대로 저장됩니다.

## 데이터와 참고 자료

실습 영상: OpenCV 저장소의 samples/data/vtest.avi (원본 파일 포함).
https://github.com/opencv/opencv/blob/4.x/samples/data/vtest.avi
OpenCV 라이선스 원문은 OPENCV_LICENSE.txt에 포함했습니다.

- 동영상 입력·출력: https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html
- 배경 차분: https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html
- MOG2 매개변수·그림자 값: https://docs.opencv.org/4.x/d7/d7b/classcv_1_1BackgroundSubtractorMOG2.html
- 윤곽선 특징: https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html
