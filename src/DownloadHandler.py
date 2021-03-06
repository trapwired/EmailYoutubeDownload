import os

import youtube_dl


def get_options(path):
    complete_path = os.path.join(path, '%(title)s.%(ext)s')
    return {
        'outtmpl': complete_path,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


class DownloadHandler(object):

    def __init__(self, path_: str, max_length_: int):
        self.path = os.path.join(path_, 'downloads')
        self.inc = 0
        self.max_length = max_length_

    def get_dir_name(self):
        res = os.path.join(self.path, 'download_' + str(self.inc))
        while os.path.exists(res):
            self.inc += 1
            res = os.path.join(self.path, 'download_' + str(self.inc))
        return res

    def download_videos(self, video_list):
        # make directory with self.inc
        directory = self.get_dir_name()
        os.mkdir(directory)
        # download videos in video_list
        with youtube_dl.YoutubeDL(get_options(directory)) as downloader:
            for link in video_list:
                dict_meta = downloader.extract_info(link, download=False)
                if dict_meta['duration'] > self.max_length * 60:
                    title = dict_meta['title'] + '.toolarge'
                    f = open(os.path.join(directory, title), "x")
                    f.close()
                else:
                    downloader.download([link])
        # return directory name
        return directory
