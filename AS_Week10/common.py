"""10주차: 고정 카메라 영상의 움직임 영역 검출과 교육용 중심점 추적."""
from pathlib import Path
from collections import deque
import csv
import cv2
import numpy as np

BASE = Path(__file__).resolve().parent

def resize_frame(frame, width=640):
    h, w = frame.shape[:2]
    return cv2.resize(frame, (width, round(h * width / w)))

def clean_mask(mask):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

def get_boxes(mask, min_area=500):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) >= min_area]

class CentroidTracker:
    """거리 기반 탐욕적 일대일 연결. 사람 인식/재식별 알고리즘은 아님."""
    def __init__(self, max_distance=60, max_missed=10):
        self.max_distance = max_distance
        self.max_missed = max_missed
        self.next_id = 0
        self.tracks = {}

    def _add(self, box, center):
        self.tracks[self.next_id] = {
            'box': box, 'center': center, 'missed': 0,
            'trail': deque([tuple(map(int, center))], maxlen=30)
        }
        self.next_id += 1

    def update(self, boxes):
        centers = np.array([(x + w / 2, y + h / 2) for x, y, w, h in boxes], dtype=float)
        old_ids = list(self.tracks)
        used_ids, used_detections = set(), set()
        if old_ids and len(centers):
            old_centers = np.array([self.tracks[i]['center'] for i in old_ids])
            distances = np.linalg.norm(old_centers[:, None, :] - centers[None, :, :], axis=2)
            candidates = sorted(
                (distances[r, c], r, c)
                for r in range(len(old_ids)) for c in range(len(centers))
                if distances[r, c] <= self.max_distance
            )
            for distance, row, column in candidates:
                track_id = old_ids[row]
                if track_id in used_ids or column in used_detections:
                    continue
                track = self.tracks[track_id]
                track.update(box=boxes[column], center=centers[column], missed=0)
                track['trail'].append(tuple(map(int, centers[column])))
                used_ids.add(track_id)
                used_detections.add(column)
        for track_id in old_ids:
            if track_id not in used_ids:
                self.tracks[track_id]['missed'] += 1
                if self.tracks[track_id]['missed'] > self.max_missed:
                    del self.tracks[track_id]
        for i, (box, center) in enumerate(zip(boxes, centers)):
            if i not in used_detections:
                self._add(box, center)
        # 현재 프레임에서 실제로 관측한 궤적만 반환한다.
        return {i: t for i, t in self.tracks.items() if t['missed'] == 0}

def paint(frame, boxes, visible=None):
    view = frame.copy()
    if visible is None:
        for x, y, w, h in boxes:
            cv2.rectangle(view, (x, y), (x + w, y + h), (0, 220, 255), 2)
    else:
        for track_id, track in visible.items():
            x, y, w, h = track['box']
            color = (40 + 47 * track_id % 190, 70 + 67 * track_id % 180, 240)
            cv2.rectangle(view, (x, y), (x + w, y + h), color, 2)
            cx, cy = map(int, track['center'])
            cv2.circle(view, (cx, cy), 4, color, -1)
            cv2.putText(view, f'ID {track_id}', (x, max(16, y - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 2)
            points = np.array(track['trail'], np.int32)
            if len(points) > 1:
                cv2.polylines(view, [points], False, color, 2)
    return view

def run(mode='tracking', video=None, show=True, max_frames=0,
        min_area=500, max_distance=60, history=150, var_threshold=25,
        snapshots=None):
    source = Path(video) if video else BASE / 'data' / 'vtest.avi'
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f'동영상을 열 수 없습니다: {source}')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not np.isfinite(fps) or fps <= 0:
        fps = 30.0
    output = BASE / 'output'
    output.mkdir(exist_ok=True)
    model = cv2.createBackgroundSubtractorMOG2(
        history=history, varThreshold=var_threshold, detectShadows=True)
    tracker = CentroidTracker(max_distance=max_distance, max_missed=10)
    previous = None
    writer = None
    count = 0
    rows = []
    snapshot_dir = Path(snapshots) if snapshots else None
    if snapshot_dir:
        snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_indices = {0, 1, 15, 30, 60, 90, 100, 120, 160, 200, 240, 300, 400, 500}
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = resize_frame(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            if mode == 'difference':
                delta = np.zeros_like(gray) if previous is None else cv2.absdiff(gray, previous)
                _, raw = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)
            else:
                raw = model.apply(frame)
                # 127인 그림자 후보는 제외하고 255인 전경 후보만 남긴다.
                _, raw_binary = cv2.threshold(raw, 200, 255, cv2.THRESH_BINARY)
                delta = None
            previous = gray.copy()
            binary = raw if mode == 'difference' else raw_binary
            mask = clean_mask(binary)
            warmup = mode != 'difference' and count < 30
            boxes = [] if warmup else get_boxes(mask, min_area)
            visible = tracker.update(boxes) if mode == 'tracking' and not warmup else None
            view = paint(frame, boxes, visible)
            if mode == 'tracking':
                h, w = frame.shape[:2]
                if writer is None:
                    writer = cv2.VideoWriter(str(output / 'tracking_result.avi'),
                        cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))
                    if not writer.isOpened():
                        raise RuntimeError('영상 저장기 생성 실패: MJPG 코덱과 경로를 확인하세요.')
                if visible:
                    for track_id, track in visible.items():
                        x, y, bw, bh = track['box']
                        cx, cy = track['center']
                        rows.append([count, round(count / fps, 3), track_id,
                                     round(float(cx), 1), round(float(cy), 1), x, y, bw, bh])
                writer.write(view)
            if snapshot_dir and count in snapshot_indices:
                prefix = snapshot_dir / f'{mode}_{count:03d}'
                for suffix, image in [('frame', frame), ('raw', raw), ('binary', binary),
                                      ('clean', mask), ('boxes', view)]:
                    cv2.imwrite(str(prefix) + '_' + suffix + '.png', image)
                if delta is not None:
                    cv2.imwrite(str(prefix) + '_delta.png', delta)
            count += 1
            if show:
                cv2.imshow('Video: q to quit', view)
                cv2.imshow('Foreground mask', mask)
                if cv2.waitKey(max(1, round(1000 / fps))) & 0xFF == ord('q'):
                    break
            if max_frames and count >= max_frames:
                break
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        if show:
            cv2.destroyAllWindows()
    if mode == 'tracking':
        with (output / 'tracks.csv').open('w', newline='', encoding='utf-8-sig') as stream:
            csv_writer = csv.writer(stream)
            csv_writer.writerow(['frame', 'time_s', 'track_id', 'cx', 'cy', 'x', 'y', 'w', 'h'])
            csv_writer.writerows(rows)
    print(f'mode={mode}, frames={count}, fps={fps:g}, observations={len(rows)}')
    return count, rows

def arguments():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default=None)
    parser.add_argument('--no-gui', action='store_true')
    parser.add_argument('--max-frames', type=int, default=0)
    parser.add_argument('--min-area', type=int, default=500)
    parser.add_argument('--max-distance', type=int, default=60)
    parser.add_argument('--history', type=int, default=150)
    parser.add_argument('--var-threshold', type=float, default=25)
    parser.add_argument('--snapshots', default=None)
    return parser.parse_args()

def launch(mode):
    a = arguments()
    run(mode, a.video, not a.no_gui, a.max_frames, a.min_area,
        a.max_distance, a.history, a.var_threshold, a.snapshots)
