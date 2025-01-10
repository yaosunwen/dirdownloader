import re
import os

import requests
from tqdm import tqdm

import typer
from typing_extensions import Annotated


app = typer.Typer(no_args_is_help=True, help='python http.server downloader')


class DirDownloader:
    def __init__(self, output_dir, overwrite=False):
        self.output_dir = output_dir
        self.overwrite = overwrite

    def download_file(self, url, filepath):
        basedir = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        temp_path = os.path.join(basedir, '__temp__.' + basename)

        if os.path.exists(filepath):
            if self.overwrite:
                os.remove(filepath)
            else:
                print(f'{filepath} exists')
                return
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        
        response = requests.get(url, stream=True)
        content_length = int(response.headers.get('content-length',0))
        with open(temp_path, mode='wb') as file, tqdm(
                desc=basename,
                total=content_length,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=1024*8):
                    size = file.write(chunk)
                    progress_bar.update(size)
        
        os.rename(temp_path, filepath)
    
    def download_dir(self, baseurl, basedir=None):
        if not basedir:
            basedir = self.output_dir
        
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        
        html = requests.get(baseurl).text
        items = re.findall('<li><a href="(.*?)">(.*?)</a></li>', html)

        for (url_path, file_name) in items:
            url = baseurl + ('' if baseurl.endswith('/') else '/') + url_path
            if file_name.endswith('/'):
                self.download_dir(url, os.path.join(basedir, file_name))
            else:
                self.download_file(url, os.path.join(basedir, file_name))


@app.command()
def main(
    url: Annotated[str, typer.Option(prompt=True)],
    output: Annotated[str, typer.Option(prompt=True)],
    overwrite: Annotated[bool, typer.Option()] = False
):
    DirDownloader(output, overwrite).download_dir(url)


if __name__ == '__main__':
    app()