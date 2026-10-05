# [TYPE:code][PROJECT:vps-deals][ROLE:static-brand-assets]
# ::RULE{纯标准库生成真实PNG社交图;不使用外部付费服务}
# ::BOUNDARY{never:把装饰图当价格证据}
from config import ROOT,load_config
import struct,zlib

def main():
    w,h=1200,630;pixels=bytearray(bytes((23,50,41))*w*h)
    def rect(x,y,rw,rh,color):
        for yy in range(y,min(y+rh,h)):
            start=(yy*w+x)*3;pixels[start:start+min(rw,w-x)*3]=bytes(color)*min(rw,w-x)
    rect(70,65,1050,3,(215,249,105));rect(870,220,210,55,(215,249,105));rect(870,310,210,55,(215,249,105))
    glyphs={'V':['10001','10001','10001','01010','00100'],'P':['11110','10001','11110','10000','10000'],'S':['01111','10000','01110','00001','11110'],'D':['11110','10001','10001','10001','11110'],'E':['11111','10000','11110','10000','11111'],'A':['01110','10001','11111','10001','10001'],'L':['10000','10000','10000','10000','11111'],'-':['00000','00000','11111','00000','00000']}
    glyphs.update({'K':['10001','10010','11100','10010','10001'],'I':['11111','00100','00100','00100','11111'],'O':['01110','10001','10001','10001','01110'],'M':['10001','11011','10101','10001','10001'],'N':['10001','11001','10101','10011','10001']})
    for line,text in enumerate(load_config()['brand'].upper().split('-')):
        x=70
        for ch in text:
            for yy,row in enumerate(glyphs[ch]):
                for xx,b in enumerate(row):
                    if b=='1':rect(x+xx*14,180+line*140+yy*20,12,18,(245,246,241))
            x+=84
    rect(70,500,680,10,(215,249,105));rect(70,545,390,5,(116,135,102))
    def chunk(k,d):return struct.pack('!I',len(d))+k+d+struct.pack('!I',zlib.crc32(k+d)&0xffffffff)
    scan=b''.join(b'\x00'+pixels[y*w*3:(y+1)*w*3] for y in range(h))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan,9))+chunk(b'IEND',b'')
    (ROOT/'assets/og.png').write_bytes(png)

if __name__=='__main__':main()
