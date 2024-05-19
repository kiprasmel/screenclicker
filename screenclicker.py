#!/usr/bin/env python

import pyautogui as pag
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract as tess
from time import sleep
import pygetwindow as gw
from mss import mss

tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def main():
    sleep(1)
    if clicktext("Search"):
	    print("text found and clicked")
    else:
	    print("text not found")

def clicktext(text):
	coords = find_text(text)
	if not coords:
		return False

	x, y, w, h = coords
	pag.click(x + w // 2, y + h // 2) 
	return True

def find_text(target_text, confidence_threshold=60):
	img = capture_active_window()

	custom_config = r'--oem 3 --psm 6'

	text_detected = tess.image_to_string(img, config=custom_config)
	print("debug: Detected Text:", text_detected)

	data = tess.image_to_data(img, output_type=tess.Output.DICT, config=custom_config)
	print(data)

	highest_confidence = -1
	best_coords = None

	for i in range(len(data['text'])):
		if int(data['conf'][i]) > confidence_threshold:
			text = data['text'][i]
			if target_text.lower() in text.lower():
				confidence = int(data['conf'][i])
				if confidence > highest_confidence:
					highest_confidence = confidence
					best_coords = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])

	return best_coords

def capture_active_window():
	active_window = gw.getActiveWindow()
	print(active_window)

	if not active_window:
		raise Exception("No active window found.")

	x, y, width, height = active_window.left, active_window.top, active_window.width, active_window.height
	with mss() as sct:
		monitor = {"left": x, "top": y, "width": width, "height": height}
		screenshot = sct.grab(monitor)
		img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
		img_ocr_ready = preprocess_image(img)
		img_ocr_ready.save("ss.png")
		return img_ocr_ready

def preprocess_image(image):
	"""
	Preprocess the image to improve OCR accuracy.
	Converts to grayscale, sharpens, and increases contrast.
	"""
	image = image.convert('L')
	image = image.filter(ImageFilter.SHARPEN)
	enhancer = ImageEnhance.Contrast(image)
	image = enhancer.enhance(2)
	return image

if __name__ == "__main__":
	main()

