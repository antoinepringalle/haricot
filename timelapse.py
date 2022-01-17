import os

from cv2 import cv2

file_format = 'jpg'
out_dir = "timelapse/"


def video_to_frames(video, path_output_dir):
	# extract frames from a video and save to directory as 'x.png' where
	# x is the frame index
	vidcap = cv2.VideoCapture(video)
	count = 0
	while vidcap.isOpened():
		success, image = vidcap.read()
		if success:
			cv2.imwrite(os.path.join(path_output_dir, '%d.' + file_format) % count, image)
			count += 1
		else:
			break
	cv2.destroyAllWindows()
	vidcap.release()


def frames_to_video(path_input_dir, video_name, fps=30, average_frames=False):
	os.system("rm -f {}*.mp4".format(out_dir))
	# choose codec according to format needed
	elements = os.listdir(path_input_dir)
	width, height = 0, 0
	if not elements:
		print("No frames in directory")
		return
	else:
		for i in range(len(elements)):
			elements[i] = elements[i][0:-4]
		elements.sort(key=int)
		print(elements)
		img = cv2.imread(path_input_dir + elements[0] + '.' + file_format)
		height, width, layers = img.shape

	# encodes frames to video with codec H264 and .avi extension
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	video = cv2.VideoWriter(out_dir + video_name + '.mp4', fourcc, fps, (width, height))

	for j in range(len(elements)):
		img = cv2.imread(path_input_dir + elements[j] + '.' + file_format)
		video.write(img)
		if average_frames:
			try:
				average_image = mean_image(path_input_dir + elements[j] + '.' + file_format,
				                           path_input_dir + elements[j + 1] + '.' + file_format)
				video.write(average_image)
			except:
				pass
	cv2.destroyAllWindows()
	print("Video created")
	video.release()


def mean_image(path_image_1, path_image_2):
	img1 = cv2.imread(path_image_1, cv2.IMREAD_COLOR)
	img2 = cv2.imread(path_image_2, cv2.IMREAD_COLOR)
	average_image = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)
	return average_image


if __name__ == '__main__':
	frames_to_video('photos/', 'video1', 20, False)
