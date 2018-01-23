import os, base64, convert, signal, json
from tornado import gen
from random import randint
import tornado, tornado.ioloop, tornado.web
from concurrent.futures import ThreadPoolExecutor

class RootHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header("Content-Type", "text/html")
        self.render("index.html")

class UploadHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        result = yield executor.submit(self.process_image)
        self.write(result)

    def process_image(self):
        random_int = randint(100000, 999999)
        file_name = str(random_int) + "_temp.png"
        with open(file_name, "wb") as file:
            file.write(base64.b64decode(self.request.body))
        encoded_latex = convert.convert(file_name, api_key)
        os.remove(file_name)
        return encoded_latex

api_key = ""
executor = ThreadPoolExecutor(max_workers=8)
app = tornado.web.Application([
        (r"/", RootHandler),
        (r"/upload", UploadHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path" : "./static"})
])

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    with open("config.json", "r") as f:
        api_key = json.loads(f.read())["api_key"]
    app.listen(80)
    print "Starting webserver..."
    tornado.ioloop.IOLoop.instance().start()
