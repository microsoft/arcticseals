# This script allows to download a single file from a remote ZIP archive
# without downloading the whole ZIP file itself.
# The hosting server needs to support the HTTP range header for it to work

import zipfile
import requests
import argparse


class HTTPIO(object):
    def __init__(self, url):
        self.url = url
        r = requests.head(self.url)
        self.size = int(r.headers['content-length'])
        assert self.size > 0
        self.offset = 0
    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.size + offset
        else:
            raise Exception('Unknown value for parameter whence')
    def read(self, size = None):     
        if size is None:
            r = requests.get(self.url, 
                             headers={"range": "bytes={}-{}".format(self.offset, self.size - 1)}, 
                             stream=True)
        else:
            r = requests.get(self.url, 
                             headers={"range": "bytes={}-{}".format(self.offset, min(self.size - 1, self.offset+size - 1))}, 
                             stream=True)
        r.raise_for_status()
        r.raw.decode_content = True
        content = r.raw.read()
        self.offset += len(content)
        return content
    def tell(self):
        return self.offset

def download_file(zip_url, relative_path, output_file):
    with zipfile.ZipFile(HTTPIO(zip_url)) as zz:
        with open(output_file, 'wb') as f:
            f.write(zz.read(relative_path))

if __name__  == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('URL', type=str, help='URL to zip file, e.g. https://example.com/myfile.zip')
    parser.add_argument('FILE_PATH', type=str, help='Path of the desired file in the ZIP file, e.g. myfolder/mydocument.docx')
    parser.add_argument('OUTPUT_FILE', type=str, help='Local path to write the file to, e.g. /home/user/mydocument.docx')
    args = parser.parse_args()
    download_file(args.URL, args.FILE_PATH, args.OUTPUT_FILE)
