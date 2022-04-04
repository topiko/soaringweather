"""
This is simple soaring weather forecast downloader.
"""
import io

from PIL import Image
from itertools import product

import requests as req
import numpy as np
import matplotlib.pyplot as plt



WEBPAGE = "http://rasp.skyltdirect.se/scandinavia/"
DAYS = ['curr', 'curr+1']
CLOCKTIMES = ['1200', '1400', '1600']
TIMES = list(product(DAYS, CLOCKTIMES))
FIGW=10
FIGH=7


class ForecastImage():

    def __init__(self):
        pass


    def make_pil_image(self, bytes_) -> Image:
        return Image.open(io.BytesIO(bytes_)).convert('RGBA')

    def get_foreground(self, *args) -> Image:

        def make_query(region: tuple[str, str],
                       forecast: tuple[str, str],
                       time: tuple[str, str]) -> str:

            reg = ''.join(region)
            forec = ''.join(forecast)
            time = '.'.join(time)
            return {'fn': f'{reg}{forec}.{time}lst.d2.png'}


        resp = req.get(url=WEBPAGE + 'getimg.php', params=make_query(*args))
        return self.make_pil_image(resp.content)

    def get_background(self, region):

        region = ''.join(region)
        resp_bg = req.get(url=WEBPAGE + f'bgmap{region}.gif')
        return self.make_pil_image(resp_bg.content)

    def set_attr(self, region, forecast, time):
        self.region = region
        self.forecast = forecast
        self.time = time

    def get_image(self, *args):

        if args:
            region, forecast, time = args
            self.set_attr(*args)
        else:
            region, forecast, time = self.region, self.forecast, self.time

        self.background = self.get_background(region)
        self.img = Image.new("RGBA", self.background.size, "WHITE")
        self.img.paste(self.background, (0,0), self.background)

        self.foreground = self.get_foreground(region, forecast, time)
        self.img.paste(self.foreground, (0,0), self.foreground)

        return self.img

    def get_meta(self):
        return self.zoom(.917,0,1,.57, self.foreground)

    def zoom(self, lower, left, upper, right, img=None):

        if img is None: img = self.img
        W, H = img.size
        lower = 1-lower
        upper = 1-upper
        lower *= H
        left *= W
        upper *= H
        right *= W

        return img.crop((left, upper, right, lower))

    def get_array(self, img=None) -> np.ndarray:

        if img is None: img = self.img
        return np.array(img)

    def make_image(self, *args) -> tuple[Image, np.ndarray]:

        self.get_image(*args)
        zoomed = self.zoom(.1, 0, .6, .6)
        meta = self.get_meta()

        zoomed.paste(meta, (0,0))

        return zoomed, np.array(zoomed)


def get_karlstad(forecast=('map', 'sw'),
                 times=TIMES):

    region = ('se', 'midsouth')

    fig, axarr = plt.subplots(len(DAYS), len(CLOCKTIMES), figsize=(FIGW, FIGH))
    for t, ax in zip(times, axarr.ravel()):
        img = ForecastImage()
        img_ = img.get_image(region, forecast, t)

        _, img_ = img.make_image()
        ax.imshow(img_)
        ax.axis('off')

    plt.tight_layout()
    plt.savefig('figs/karlstad.png')
    return fig

if __name__ == "__main__" :

    get_karlstad()
    plt.show()
