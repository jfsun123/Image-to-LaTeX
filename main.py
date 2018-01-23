import os, base64, convert
from tornado import gen
from random import randint
import tornado, tornado.ioloop, tornado.web

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type","text/html")
        self.render("index.html")

class UploadHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        result = yield self.processImg()
        self.write(result)
        self.finish()

    @gen.coroutine
    def processImg(self):
        random_int = randint(1000, 9999)
        file_name = str(random_int) + "_temp.png"
        with open(file_name, "wb") as file:
            file.write(base64.b64decode(self.request.body))

        encoded_latex = convert.convert(file_name)
        os.remove(file_name)

        raise gen.Return(encoded_latex)


app = tornado.web.Application([
        (r"/", RootHandler),
        (r"/upload", UploadHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path" : "./static"})
])

if __name__ == "__main__":
    print "Starting Image LaTeX Converter."
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    
