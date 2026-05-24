"""静态文件服务器 + API 代理 + gzip + 缓存"""
import http.server
import urllib.request
import os
import gzip
import io
import mimetypes

PORT = 5173
DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
BACKEND = 'http://localhost:8000'

CACHE_FOREVER = ['assets/', 'favicon']  # 带 hash 的文件永久缓存


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/'):
            return self._proxy()
        # SPA fallback
        file_path = self.translate_path(self.path)
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy()
        else:
            super().do_POST()

    def do_PUT(self):
        self._proxy() if self.path.startswith('/api/') else self.send_error(405)

    def do_DELETE(self):
        self._proxy() if self.path.startswith('/api/') else self.send_error(405)

    def end_headers(self):
        # 缓存头
        for prefix in CACHE_FOREVER:
            if prefix in self.path:
                self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
                break
        # gzip 支持
        accept_encoding = self.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding and self.path.endswith(('.js', '.css', '.html', '.svg')):
            self.send_header('Content-Encoding', 'gzip')
        super().end_headers()

    def send_header(self, keyword, value):
        super().send_header(keyword, value)

    def copyfile(self, source, outputfile):
        """重写以支持 gzip 压缩"""
        accept_encoding = self.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding and self.path.endswith(('.js', '.css', '.html', '.svg')):
            buf = io.BytesIO()
            gz = gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6)
            while True:
                chunk = source.read(65536)
                if not chunk:
                    break
                gz.write(chunk)
            gz.close()
            outputfile.write(buf.getvalue())
        else:
            super().copyfile(source, outputfile)

    def _proxy(self):
        url = BACKEND + self.path
        cl = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(cl) if cl > 0 else None
        req = urllib.request.Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ('host', 'content-length'):
                req.add_header(k, v)
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() != 'transfer-encoding':
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args):
        print(f'{self.address_string()} - {fmt % args}')


if __name__ == '__main__':
    print(f'http://0.0.0.0:{PORT}  (gzip on)')
    http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler).serve_forever()
