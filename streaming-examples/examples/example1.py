import asyncio.streams
import codecs
from codecs import StreamReader
import sys
from typing import Iterable

source_text = '0123456789' * 21
source_bytes = source_text.encode()


def text_writer(text: str, blksiz=16, encoding='utf8') -> Iterable[bytes]:
    encoder = codecs.getincrementalencoder(encoding)()
    start, end = 0, blksiz
    while start < len(text):
        final = end >= len(text)
        buf = encoder.encode(text[start:end], final)
        yield buf
        start = end
        end += blksiz


def text_reader(source: Iterable[bytes], encoding='utf8') -> Iterable[str]:
    decoder = codecs.getincrementaldecoder(encoding)()
    for buf in source:
        yield decoder.decode(buf, False)
    remaining = decoder.decode(b'', True)
    if remaining != '':
        yield remaining


writer = text_writer(source_text)
reader = text_reader(writer)

dest_text = ''
for part in reader:
    dest_text += part

assert source_text == dest_text

print('Done')
