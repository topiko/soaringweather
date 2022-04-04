"""
This is simple soaring weather forecast downloader.
"""
import re
import io

from PIL import Image
import requests as req
import numpy as np
import matplotlib.pyplot as plt



WEBPAGE = "http://rasp.skyltdirect.se/scandinavia/"

regions = [('se', 'midsouth')]
forecasts = [('map','sw')]
times = [('curr+1','1500')]

class ForecastImage():

    def __init__(self):
        pass


    def make_query(self,
                   region: tuple[str, str],
                   forecast: tuple[str, str],
                   time: tuple[str, str]) -> str:

        reg = ''.join(region)
        forec = ''.join(forecast)
        time = '.'.join(time)
        return {'fn': f'{reg}{forec}.{time}lst.d2.png'}

    def handle_img(self, bytes_) -> Image:
        return Image.open(io.BytesIO(bytes_)).convert('RGBA')

    def foreground(self, *args) -> Image:

        resp = req.get(url=WEBPAGE + 'getimg.php', params=self.make_query(*args))
        return self.handle_img(resp.content)

    def get_image(self, region, forecast, time):

        resp_bg = req.get(url=WEBPAGE + 'bgmap{}.gif'.format(''.join(region)))
        self.img = self.handle_img(resp_bg.content)

        foreground = self.foreground(region, forecast, time)
        self.img.paste(foreground, (0,0), foreground)

        return self.img

    def get_array(self) -> np.ndarray:

        return np.array(self.img)


if __name__ == "__main__" :

    img = ForecastImage()
    img_ = img.get_image(regions[0], forecasts[0], times[0])
    img_.show()

    img = img.get_array()
    plt.imshow(img)
    plt.axis('off')
    plt.show()
