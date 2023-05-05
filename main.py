from matplotlib import pyplot as plt
import StringImage
import os

path = "input/"
imgPath = "input/" + os.listdir(path)[0]
img_path = "2.jpg"
radius = 500
nPins = 240
nLines = 6000

# Usage
if __name__ == '__main__' :
  converter = StringImage(img_path, radius, nPins)
  img_res = converter.Convert(max_lines = nLines)
  plt.imshow(img_res, cmap='gray')
  plt.show()