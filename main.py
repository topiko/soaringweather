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
        #self.img.paste(self.background, (0,0), self.background)

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

    def make_image(self, *args, zoom=None) -> tuple[Image, np.ndarray]:

        img = self.get_image(*args)
        if zoom is not None:
            zoomed = self.zoom(*zoom, img)
        meta = self.get_meta()

        zoomed.paste(meta, (0,0))

        return zoomed, np.array(zoomed.convert('RGBA'))

    @property
    def color_table(self):
        self._color_table = {'<1m/s': np.array([231,231,255,233]),
                             '(1-2)m/s':np.array([211, 246, 211, 219]),
                             '(2-2.5)m/s':np.array([255, 255, 161,196]),
                             '(2.5-3)m/s':np.array([255, 208, 161, 196])} #,
                             #'(3-4)m/s':np.array([]),
                             #'>4m/s':np.array([])}

        return self._color_table
import matplotlib.patches as patches
from matplotlib.colors import to_rgb


def get_karlstad(forecast=('map', 'sw'),
                 times=TIMES):

    region = ('se', 'midsouth')

    fig, axarr = plt.subplots(len(DAYS), len(CLOCKTIMES), figsize=(FIGW, FIGH))
    _, axarr2 = plt.subplots(len(DAYS), len(CLOCKTIMES), figsize=(FIGW, FIGH))
    img = ForecastImage()
    for t, ax, ax2 in zip(times, axarr.ravel(), axarr2.ravel()):
        img_ = img.get_image(region, forecast, t)

        pil_img, img_ = img.make_image(zoom=(.1, 0, .6, .6))


        c, ccount = np.unique(img_.reshape(-1, 4), axis=0, return_counts=True)

        sidx = ccount.argsort()[::-1][:20]
        ax2.bar(range(len(sidx)), ccount[sidx], color=c[sidx]/255)
        for ix, sid in enumerate(sidx):
            ax2.text(ix, ccount[sid], c[sid], rotation=90)

        pick_colors = np.array(list(img.color_table.values()))
        mask = np.isin(c, pick_colors).all(axis=1)
        N = ccount.sum()

        c = c[mask]
        ccount = ccount[mask]

        # TODO: there must be a better way :(
        ccarr = np.zeros(len(pick_colors))
        for i, pc in enumerate(pick_colors):
            mask = (c==pc).all(axis=1)
            if mask.sum() == 1:
                ccarr[i] = ccount[mask]/N



        ax.imshow(img_)
        axins = ax.inset_axes([0., 0., 0.6, 0.3])
        axins.bar(range(len(pick_colors)), ccarr, color=pick_colors/255, edgecolor='black')
        axins.set_xticks(range(len(pick_colors)))
        axins.set_xticklabels(list(img.color_table.keys()), rotation=45, fontsize=8)
        axins.patch.set_alpha(0.5)
        axins.set_ylim([0,.5])


        ax.axis('off')

    plt.tight_layout()
    #plt.savefig('figs/karlstad.png')
    return fig

if __name__ == "__main__" :

    get_karlstad()

    plt.show()
