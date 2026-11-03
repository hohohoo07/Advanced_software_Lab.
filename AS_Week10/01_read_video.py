from pathlib import Path
import argparse
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('--no-gui', action='store_true')
args = parser.parse_args()
video = Path(__file__).resolve().parent / 'data' / 'vtest.avi'
cap = cv2.VideoCapture(str(video))
if not cap.isOpened():
    raise RuntimeError(f'동영상을 열 수 없습니다: {video}')
fps = cap.get(cv2.CAP_PROP_FPS)
print('fps =', fps)
print('frame_count =', int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
print('size =', int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
count = 0
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if not args.no_gui:
            cv2.imshow('video: q to quit', frame)
            if cv2.waitKey(max(1, round(1000 / (fps or 30)))) & 0xFF == ord('q'):
                break
finally:
    cap.release()
    if not args.no_gui:
        cv2.destroyAllWindows()
print('read_frames =', count)
