import os
import cv2 as cv

print("Current Working Directory:", os.getcwd())
print("Absolute Path:", os.path.abspath('sudoku.png'))

img = cv.imread(os.path.abspath('sudoku.png'))
if img is None:
    print("Image not found or unable to load.")
else:
    cv.imshow("Display window", img)
    cv.waitKey(0)
    cv.destroyAllWindows()
