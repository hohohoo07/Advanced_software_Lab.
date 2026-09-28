import cv2
import numpy as np

# 1. 이미지 로드
image = cv2.imread('images/input.jpg')
if image is None:
    print("오류: images/input.jpg 파일을 찾을 수 없습니다.")
    exit()

# 2. 필터 적용 (실습 1~4 종합)
# 평균 필터 (3x3, 5x5, 9x9)
blur3 = cv2.blur(image, (3, 3))
blur5 = cv2.blur(image, (5, 5))
blur9 = cv2.blur(image, (9, 9))

# 가우시안 필터
gaussian = cv2.GaussianBlur(image, (5, 5), 0)

# 미디언 필터
median = cv2.medianBlur(image, 5)

# 샤프닝 필터
kernel = np.array([
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0]
])
sharpened = cv2.filter2D(image, -1, kernel)

# 3. 결과 이미지 results 폴더에 저장
cv2.imwrite('results/blur5.jpg', blur5)
cv2.imwrite('results/gaussian.jpg', gaussian)
cv2.imwrite('results/median.jpg', median)
cv2.imwrite('results/sharpened.jpg', sharpened)

# 4. 화면 출력 (확인용)
cv2.imshow('Original', image)
cv2.imshow('Sharpened', sharpened)

cv2.waitKey(0)
cv2.destroyAllWindows()