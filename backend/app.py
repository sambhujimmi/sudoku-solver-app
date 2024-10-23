import cv2
import numpy as np
import pytesseract
from PIL import Image
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)

# sudoku size
n = 9
# box size
m = 3


def find_puzzle(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    puzzle_contour = max(contours, key=cv2.contourArea)
    return cv2.boundingRect(puzzle_contour)

def perpesctive_transform(image, processed):
    puzzle_rect = find_puzzle(processed)
    x, y, w, h = puzzle_rect
    # print(puzzle_rect)
    pts1 = np.float32([[x,y],[x+w,y],[x,y+h],[x+w, y+h]])

    rows = int(pts1[1][0] - pts1[0][0])
    cols = int(pts1[2][1] - pts1[0][1])
    # rows = cols = 300

    pts2 = np.float32([[0,0],[rows,0],[0,cols],[rows,cols]])

    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(processed,M,(rows,cols))

    pts = np.array([[x,y],[x,y+h],[x+w,y+h],[x+w,y]], np.int32)
    pts = pts.reshape((-1,1,2))

    cv2.polylines(image,[pts],True,(255,255,0))
    # cv2.imshow("pic", image)
    # cv2.imshow("pic", dst)
    return dst

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    # cv2.imshow("pic", thresh)
    return cv2.bitwise_not(thresh)

def remove_lines(image):
    line_size = int(image.shape[0]/10)
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (line_size,1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,line_size))
    h_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, h_kernel)
    v_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, v_kernel)
    lines = cv2.add(h_lines, v_lines)
    lines = cv2.dilate(lines, cv2.getStructuringElement(cv2.MORPH_RECT, (7,7)))
    lines_mask = cv2.bitwise_not(lines)
    # cv2.imshow("pic", lines_mask)
    return cv2.bitwise_and(image, lines_mask)

def extract_cells(image, puzzle_rect):
    x, y, w, h = puzzle_rect
    cell_width, cell_height = w // n, h // n
    cells = []
    for i in range(n):
        for j in range(n):
            cell = image[y + i*cell_height : y + (i+1)*cell_height,
                         x + j*cell_width : x + (j+1)*cell_width]
            # if i == 0 and j == 4:
                # cv2.imshow("pic", cell)
                # print(f"Bound = {y + i*cell_height} : {y + (i+1)*cell_height}, {x + j*cell_width} : {x + (j+1)*cell_width}")
            cells.append(cell)
    return cells

def is_cell_empty(cell, threshold=0.02):
    if cell is None:
        return True
    total_pixels = cell.shape[0] * cell.shape[1]
    non_zero_pixels = cv2.countNonZero(cell)
    # print(f"Threshold = {non_zero_pixels / total_pixels}")
    return (non_zero_pixels / total_pixels) < threshold

def preprocess_cell(cell):
    if cell is None:
        return np.zeros((28, 28), dtype=np.uint8)

    w = cell.shape[1]
    h = cell.shape[0]
    pad_w = int(0.1*w)
    # pad_h = int(0.1*h)
    pad_h = 0
    cell = cell[pad_h:h-pad_h, pad_w:w-pad_w]

    # Apply morphological operations to clean up the image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # cell = cv2.erode(cell, kernel, iterations=1)
    cell = cv2.morphologyEx(cell, cv2.MORPH_OPEN, kernel)

    # Resize to a consistent size
    cell = cv2.resize(cell, (28, 35), interpolation=cv2.INTER_LINEAR)

    # Add padding
    padding = 10
    cell = cv2.copyMakeBorder(cell, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=0)

    cell = cv2.GaussianBlur(cell, (3,3), 0)

    cell = cv2.bitwise_not(cell)

    # cv2.imshow("pic", cell)
    return cell

def recognize_digit(cell):
    cell = preprocess_cell(cell)

    # Convert to PIL Image
    cell_pil = Image.fromarray(cell)

    # Use Tesseract to do OCR on the cell
    config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
    digit = pytesseract.image_to_string(cell_pil, config=config).strip()

    return int(digit) if digit.isdigit() else None

##########################################################################################################################################################

def check(sudoku, row, col, val):
    # row and col
    for i in range(n):
        if sudoku[row][i] == val or sudoku[i][col] == val:
            return False
    # box
    boxrow = (row//m)*m
    boxcol = (col//m)*m
    for i in range(boxrow, boxrow+m):
        for j in range(boxcol, boxcol+m):
            if sudoku[i][j] == val:
                return False
    return True

def possibles(sudoku, i, j):
    possible_nums = []
    for v in range(1, n+1):
        if check(sudoku, i, j, v):
            possible_nums.append(v)
    return possible_nums

def solver(sudoku):
    empty = {}
    for i in range(8, -1, -1):
        for j in range(8, -1, -1):
            if sudoku[i][j] == 0:
                possible_nums = possibles(sudoku, i, j)
                if len(possible_nums) < 1:
                    print("\nImpossible to solve\n")
                elif len(possible_nums) == 1:
                    sudoku[i][j] = possible_nums[0]
                else:
                    empty[(i, j)] = possible_nums
    # backtracking
    pos = [x for x in empty]
    
    i = 0
    while i < len(pos):
        row = pos[i][0]
        col = pos[i][1]
        val = sudoku[row][col]
        possible_nums = empty[pos[i]]
        if val == 0:
            num_index = 0
        elif val == possible_nums[-1]:
            sudoku[row][col] = 0
            i -= 1
            continue
        else:
            num_index = possible_nums.index(val)+1
        
        for j in range(num_index, len(possible_nums)):
            num = possible_nums[j]
            if check(sudoku, row, col, num):
                sudoku[row][col] = num
                i += 1
                break
            elif j == len(possible_nums)-1:
                sudoku[row][col] = 0
                i -= 1
    return np.array(sudoku)

def process_sudoku(image):
    processed = preprocess_image(image)
    transformed = perpesctive_transform(image, processed)
    puzzle_rect = find_puzzle(transformed)
    digits = remove_lines(transformed)
    cells = extract_cells(digits, puzzle_rect)


    sudoku_grid = []
    for i, cell in enumerate(cells):
        # print(f"Cell {i}")
        if is_cell_empty(cell):
            sudoku_grid.append(0)
        else:
            digit = recognize_digit(cell)
            if digit is not None:
                sudoku_grid.append(digit)
            else:
                sudoku_grid.append(0)

    # Print the recognized Sudoku grid
    sudoku_grid = np.array(sudoku_grid)
    sudoku_grid.resize(n,n)

    return sudoku_grid

##########################################################################################################################################################

@app.route("/")
def index_page():
    return render_template('test.html')

@app.route("/test", methods = ['POST'])
def test():
    print(request.form['image'].json)
    # base64_image = request.get_data().split(b';base64,')[1].split(b'\r\n')[0]
    return jsonify({"result": "success"})

@app.route("/upload", methods = ['POST'])
def image_upload():
    if not request.files:
        if 'image' in request.form:
            # Read the base64 image
            base64_image = request.form['image']
            if ('data:' in base64_image):
                base64_image = base64_image.split(';base64,')[1]
            base64_bytes = base64.b64decode(base64_image)
            nparr = np.frombuffer(base64_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the image
            result_matrix = process_sudoku(image).tolist()
            return jsonify({'result': result_matrix})
        
        return jsonify({'error': 'No image file provided'}), 400
    
    # if file.filename == '':
    #     return jsonify({'error': 'No file selected'}), 400
    
    if 'image' in request.files:
        # Read the image file
        file = request.files['image']
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the image
        result_matrix = process_sudoku(image).tolist()
        return jsonify({'result': result_matrix})
    return jsonify({'error': 'No image file provided'}), 400

@app.route("/solve", methods=['POST'])
def solve_sudoku():
    data = request.json
    if 'sudoku' not in data:
        return jsonify({'error': 'No sudoku provided'}), 400
    
    sudoku = data['sudoku']
    
    # Validate input
    if not isinstance(sudoku, list) or not all(isinstance(row, list) for row in sudoku):
        return jsonify({'error': 'Invalid matrix format'}), 400
    
    # Solve sudoku
    solution = solver(sudoku).tolist()
    
    return jsonify({'result': solution})

# main(os.path.abspath('sudoku4.jpg'))