import sys, os
import cv
import cv2
import xml.etree.ElementTree as ET
import base64
import numpy
import csv
import Image
import shutil # require to copy and paste the file
#import smart_verity_gui as gui #MESSAGE: My miserable attempt at making a GUI. I trust you will fare better. 

working_folder = os.curdir


#HAAR_CASCADE_PATH = "C:\\OpenCV2.3\\data\\haarcascades\\haarcascade_frontalface_alt.xml"
HAAR_CASCADE_PATH = "C:\\OpenCV\\opencv\\data\\haarcascades\\haarcascade_frontalface_alt.xml"
#HAAR_CASCADE_PATH = '/home/edu/work/odesk/idris/haar/haarcascade_frontalface_alt.xml'

def main():
	#MESSAGE: Run batch process. GUI will help specify which function should run
	batch_process(working_folder + '/pm_samples') 
	#MESSAGE: single_process(xml_file) #Will be activated when GUI has been built to activate single XML functionality

def batch_process(folder_path):

	#Store all the xml files in a folder in this list
	subscribers = os.listdir(folder_path)

	#CSV file where result will be written to.
	#writer = csv.writer(open(folder_path+"/../detect_results.csv", "wb"))
	#writer.writerow(['subscriber_filename','fep_tracking_id','mobile_number','image_verification','details'])

	for subscriber in subscribers:
#		print subscriber
		#MESSAGE: This picks each xml file and parses it.
		file_path = folder_path+"/"+subscriber
		tree = ET.parse(file_path)  
		root = tree.getroot()
		fepid = root[0].text #MESSAGE: This fetches the unique id of the subscriber
		number = root[1].text #MESSAGE: This fetches the phone number of subscriber
		imagevr = facedetect(root[2].text) #MESSAGE: This calls the facedetect function. Pass the subscriber's image dump as the argument.
		face_count = len(imagevr)
		if face_count == 1:
			detect = 1
			reason = imagevr
#			print imagevr
			image_path = working_folder+"/processed/" +fepid+".jpg"
			xml_file_path = working_folder+"/processed/" +subscriber
			fh = open(image_path, "wb")
			fh.write(root[2].text.decode('base64'))
			fh.close()
			crop_image_open = Image.open(image_path)
			output_img = crop_image_open.crop((imagevr[0][0]-13,
											 imagevr[0][1]-33, 
											 imagevr[0][2]+imagevr[0][0]+20, 
											 imagevr[0][3]+imagevr[0][1]+50))
			output_img.save(working_folder+"/cropped/" +fepid+".jpg")
			shutil.copy2(file_path, xml_file_path)
		else:
			detect = 0
			if face_count < 1:
				image_path = working_folder+"/reject/" +fepid+".jpg"
				xml_file_path = working_folder+"/reject/" +subscriber
				fh = open(image_path, "wb")
				fh.write(root[2].text.decode('base64'))
				fh.close()
				shutil.copy2(file_path, xml_file_path)
				reason = "No face detected"
			if face_count > 1:
				image_path = working_folder+"/reject/" +fepid+".jpg"
				xml_file_path = working_folder+"/reject/" +subscriber
				fh = open(image_path, "wb")
				fh.write(root[2].text.decode('base64'))
				fh.close()
				shutil.copy2(file_path, xml_file_path)
				reason = str(face_count) + " faces detected"
		
#		writer.writerow([subscriber, fepid, number, detect, reason]) 

def single_process(xml_file):
	#MESSAGE: This function will extract details of the user from the XML file. For the "Process single XML page"
	#MESSAGE: The xml file will be specified by the GUI
	pass

def get_image(image_dump):
	#MESSAGE: This function will be used to fetch the image that will be displayed in the "Process Single XML page"
	#MESSAGE: The subscribers image will have a rectangle drawn on it using coordinates returned by the facedetect() function.
	pass

def process_format():
	#MESSAGE: This function returns the format that we want to use. 
	#MESSAGE: Design a dropdown for it in the GUI. And make it return whatever is selected. 
	#MESSAGE: Put three options: Option 1, Option 2, and Option 3.
	#MESSAGE: I will be writing the required code in the future. 
	pass


def decode_image(image):
	return base64.decodestring(image)

def facedetect(image_dump):
#	print image_dump
	storage = cv.CreateMemStorage()
#	print HAAR_CASCADE_PATH
	cascade = cv.Load(HAAR_CASCADE_PATH)
	image_dump = decode_image(image_dump)
	image_buf = numpy.frombuffer(image_dump,dtype=numpy.uint8)
	image_numpy = cv2.imdecode(image_buf, cv.CV_LOAD_IMAGE_GRAYSCALE)
	image_numpy = cv2.equalizeHist(image_numpy)
	image = cv.fromarray(image_numpy)
	#original_image = image = cv.LoadImage('babes.jpg', cv.CV_BGR2GRAY)
	#image = cv.CreateImage(cv.GetSize(original_image), cv.IPL_DEPTH_64F, 10 );
	#cv.Smooth(original_image, image, cv.CV_BLUR_NO_SCALE, 3)
	faces = []

	#MESSAGE: The last five arguments of this function are subject to change based on what is returned by the process_format() function.
	#MESSAGE: This is just for information sake. Not critical to the project. 
	detected = cv.HaarDetectObjects(image, cascade, storage, 1.09988999, 4, cv.CV_HAAR_DO_CANNY_PRUNING, (10,10))
	

	if detected:
		for (x,y,w,h),n in detected:
			faces.append((x,y,w,h))
#	showimage(faces, image) #MESSAGE: Commented out intentionally. Only use if you want to test the showimage() function for any reason whatsoever
	return faces

#MESSAGE: This function is for diplaying images on the screen using OpenCV's internal function. It is not necessary for this project. 
def showimage(faces, image):
	i = 0
	c = -1
	while (c==-1):
		for (x,y,w,h) in faces:
			cv.Rectangle(image, (x,y), (x+w,y+h), 255)
		cv.ShowImage("Picture", image)
		i += 1
		c=cv.WaitKey(10)

if __name__ == "__main__":
	main()
