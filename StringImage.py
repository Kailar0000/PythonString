import numpy as np
from PIL import Image, ImageFont, ImageDraw
import random
from tqdm import tqdm


class StringImage:
    def __init__(self, img_path, radius, nPins):
        self.radius = radius
        self.nPins = nPins
        self.img, self.img_res = self.PrepareImage(img_path, radius)
        self.PinPos = self.PreparePins(radius, nPins)
        self.Lines = []

    def PrepareImage(self, img_path, radius):
        im_t = Image.open(img_path).convert('L')
        w, h = im_t.size
        min_dim = min(h, w)
        top = int((h - min_dim) / 2)
        left = int((w - min_dim) / 2)
        im_croped = im_t.crop((left, top, left + min_dim, top + min_dim)).resize((radius * 2 + 1, radius * 2 + 1))
        img = np.asarray(im_croped).copy()
        y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
        mask = x ** 2 + y ** 2 > radius ** 2
        img[mask] = 255
        img = 255 - img  # negative image

        img_res = np.ones(img.shape) * 255
        return img, img_res

    def PreparePins(self, radius, nPins):
        alpha = np.linspace(0, 2 * np.pi, nPins + 1)
        PinPos = []
        for angle in alpha[0:-1]:
            x = int(radius + radius * np.cos(angle))
            y = int(radius + radius * np.sin(angle))
            # adding noise to Pin Positions in order to reduce Moire effect
            if x > 5:
                x = x - random.randint(0, 5)
            elif x < (2 * radius - 5):
                x = x + random.randint(0, 5)
            if y > 5:
                y = y - random.randint(0, 5)
            elif y < (2 * radius - 5):
                y = y - random.randint(0, 5)
            PinPos.append((x, y))
        return PinPos

    def getLineMask(self, pin1, pin2):
        length = int(np.hypot(pin2[0] - pin1[0], pin2[1] - pin1[1]))
        x = np.linspace(pin1[0], pin2[0], length)
        y = np.linspace(pin1[1], pin2[1], length)
        return (x.astype(np.intc) - 1, y.astype(np.intc) - 1)

    def LineScore(self, line):
        score = np.sum(line)
        score = score / (line.shape[0] + 0.001)  # add 0.001 to avoid divide by 0 error
        # penalty = sum(line<=10)
        # score = 0.6*score + 0.4*penalty
        score_mean = np.mean(line) if len(line) > 0 else 0
        return score, score_mean

    def FindBestNextPin(self, currentPin):
        bestScore = -999999
        bestPin = -1
        bestMean = 0
        for p in range(self.nPins - 1):
            nextPin = (p + currentPin) % self.nPins
            if abs(currentPin - nextPin) < 10: continue
            if (currentPin, nextPin) in self.Lines: continue
            tx, ty = self.getLineMask(self.PinPos[currentPin], self.PinPos[nextPin])
            tempLine = self.img[tx, ty]
            tempScore, tempMean = self.LineScore(tempLine)
            if tempScore > bestScore:
                bestScore = tempScore
                bestPin = nextPin
                bestMean = tempMean
        return bestPin, bestMean

    def SaveImage(self, image_matrix, file_path, description, color=(255, 0, 0), position=(10, 10)):
        imtemp = Image.fromarray(image_matrix).convert('RGB')
        drawer = ImageDraw.Draw(imtemp)
        font = ImageFont.truetype("font.ttf", 36)
        drawer.text(position, description, color, font=font)
        imtemp.save(file_path)

    def Convert(self, max_lines=2000):
        currentPin = random.randint(0, self.nPins)
        for l in tqdm(range(max_lines)):
            bestPin, bestMean = self.FindBestNextPin(currentPin)
            self.Lines.append((currentPin, bestPin))
            tx, ty = self.getLineMask(self.PinPos[currentPin], self.PinPos[bestPin])
            self.img[tx, ty] = np.maximum(self.img[tx, ty] - bestMean, 0)
            self.img_res[tx, ty] = np.maximum(self.img_res[tx, ty] - bestMean, 0)
            currentPin = bestPin
        return self.img_res